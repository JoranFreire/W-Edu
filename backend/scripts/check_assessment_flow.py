"""Exercise grading schemes, assessment plan, grades, class diary, period closing and final results (phase 13).

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_assessment_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import anyio.to_thread
import fastapi.routing
import httpx
import starlette.concurrency
import starlette.routing

from scripts.check_support import MISSING_ID, ApiClient  # noqa: E402
import app.models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.core.tenancy import bind_institution
from app.models.institution import Institution, InstitutionMembership
from app.models.notification import NotificationEvent, NotificationEventType
from app.models.lesson import Lesson
from app.models.quiz import Quiz, QuizAttempt
from app.models.schedule import AttendanceRecord, AttendanceStatus, ScheduledMeeting
from app.models.student import Student, UserRole
from app.schemas.assessment import GradingSchemeOut
from app.services.assessment.result_rules import decide
from main import app


async def run_in_threadpool_inline(func, *args, **kwargs):
    kwargs.pop("abandon_on_cancel", None)
    kwargs.pop("cancellable", None)
    kwargs.pop("limiter", None)
    return func(*args, **kwargs)


fastapi.routing.run_in_threadpool = run_in_threadpool_inline
starlette.concurrency.run_in_threadpool = run_in_threadpool_inline
starlette.routing.run_in_threadpool = run_in_threadpool_inline
anyio.to_thread.run_sync = run_in_threadpool_inline

PASSWORD = "secret123"
USERS = (
    ("admin", UserRole.institution_admin),
    ("coord", UserRole.coordinator),
    ("prof", UserRole.instructor),
    ("outro", UserRole.instructor),
    ("ana", UserRole.student),
    ("bia", UserRole.student),
)


def seed() -> tuple[int, dict[str, int]]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="escola", name="Escola")
        db.add(institution)
        db.flush()
        for name, role in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
            ids[name] = str(user.id)
        institution_id = institution.id
        db.commit()
    return institution_id, ids


def seed_quiz_and_meeting(institution_id: int, course_id: int, offering_id: int, ids: dict[str, int]) -> tuple[int, int]:
    """Quiz com tentativas (Ana: 80 e 90) e encontro em que Ana faltou."""
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        lesson = Lesson(course_id=course_id, title="Aula quiz")
        db.add(lesson)
        db.flush()
        quiz = Quiz(lesson_id=lesson.id)
        db.add(quiz)
        db.flush()
        for score in (80, 90):
            db.add(QuizAttempt(student_id=ids["ana"], quiz_id=quiz.id, score=score, passed=True, answers={},
                               attempted_at=datetime(2027, 3, 1, 10, score % 60, tzinfo=timezone.utc)))
        meeting = ScheduledMeeting(class_offering_id=offering_id, title="Aula 3",
                                   starts_at=datetime(2027, 3, 12, 8, tzinfo=timezone.utc), ends_at=datetime(2027, 3, 12, 10, tzinfo=timezone.utc))
        db.add(meeting)
        db.flush()
        db.add(AttendanceRecord(scheduled_meeting_id=meeting.id, class_offering_id=offering_id, student_id=ids["ana"], status=AttendanceStatus.absent))
        db.commit()
        return quiz.id, meeting.id


class Checker:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    async def login(self, name: str) -> dict:
        response = await self.client.post("/auth/login", json={"email": f"{name}@example.com", "password": PASSWORD})
        assert response.status_code == 200, f"login {name}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def call(self, method: str, path: str, expected: int, message: str, headers: dict, **kwargs):
        response = await self.client.request(method, path, headers=headers, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else {}


async def setup_structure(c: Checker, h: dict[str, dict], ids: dict[str, int]) -> dict:
    """Esquema padrao, periodo com duas etapas, turma-grupo com duas alunas e oferta ministrada por 'prof'."""
    admin, coord = h["admin"], h["coord"]
    concepts = [{"code": "A", "min_value": 9}, {"code": "B", "min_value": 7}, {"code": "C", "min_value": 5}, {"code": "D", "min_value": 0}]
    await c.call("POST", "/assessment/grading-schemes", 201, "default scheme", coord,
                 json={"name": "Conceitos", "scale": "concept", "concepts": concepts, "is_default": True})
    await c.call("POST", "/assessment/grading-schemes", 409, "duplicate scheme name", coord, json={"name": "Conceitos"})
    await c.call("POST", "/assessment/grading-schemes", 422, "passing grade outside scale", coord, json={"name": "X", "passing_grade": 11})
    await c.call("POST", "/assessment/grading-schemes", 403, "instructor cannot create scheme", h["prof"], json={"name": "Y"})

    term = await c.call("POST", "/academic/terms", 201, "term", coord, json={"name": "2027", "starts_on": "2027-02-01", "ends_on": "2027-12-15"})
    await c.call("POST", f"/academic/terms/{term['id']}/status", 200, "open term", coord, json={"status": "open"})
    p1 = await c.call("POST", f"/academic/terms/{term['id']}/grading-periods", 201, "period 1", coord,
                      json={"name": "1º bimestre", "starts_on": "2027-02-01", "ends_on": "2027-04-30"})
    p2 = await c.call("POST", f"/academic/terms/{term['id']}/grading-periods", 201, "period 2", coord,
                      json={"name": "2º bimestre", "starts_on": "2027-05-01", "ends_on": "2027-07-09"})
    other = await c.call("POST", "/academic/terms", 201, "other term", coord, json={"name": "2028", "starts_on": "2028-02-01", "ends_on": "2028-12-15"})
    foreign_period = await c.call("POST", f"/academic/terms/{other['id']}/grading-periods", 201, "other term period", coord,
                                  json={"name": "B1", "starts_on": "2028-02-01", "ends_on": "2028-04-30"})

    program = await c.call("POST", "/academic/programs", 201, "program", coord, json={"code": "EF", "name": "Fundamental", "level": "basic"})
    subject = await c.call("POST", "/academic/subjects", 201, "subject", coord, json={"code": "MAT", "name": "Matemática", "hours": 160})
    curriculum = await c.call("POST", f"/academic/programs/{program['id']}/curricula", 201, "curriculum", coord, json={"version": "1"})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/components", 201, "component", coord, json={"subject_id": subject["id"], "term_number": 6})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, "activate", coord)
    group = await c.call("POST", "/academic/class-groups", 201, "group", coord, json={"program_id": program["id"], "term_id": term["id"], "name": "6A"})
    for name in ("ana", "bia"):
        enrollment = await c.call("POST", "/academic/program-enrollments", 201, f"enroll {name}", coord,
                                  json={"student_id": ids[name], "program_id": program["id"]})
        await c.call("POST", f"/academic/class-groups/{group['id']}/members", 201, f"allocate {name}", coord,
                     json={"program_enrollment_id": enrollment["id"]})

    course = await c.call("POST", "/courses", 201, "course", coord, json={"name": "Matemática EAD"})
    offering = await c.call("POST", "/schedule/classes", 201, "offering", coord, json={
        "course_id": course["id"], "name": "Matemática 6A", "capacity": 40, "instructor_id": ids["prof"],
        "starts_at": "2027-02-01T07:00:00Z", "ends_at": "2027-12-15T12:00:00Z",
        "class_group_id": group["id"], "subject_id": subject["id"],
    })
    await c.call("PATCH", f"/schedule/classes/{offering['id']}", 404, "unknown grading scheme", coord, json={"grading_scheme_id": MISSING_ID})
    synced = await c.call("POST", f"/assessment/offerings/{offering['id']}/sync-group-enrollments", 200, "sync group", coord)
    c.expect(synced.get("created") == 2, f"group members enrolled in offering: {synced}")
    again = await c.call("POST", f"/assessment/offerings/{offering['id']}/sync-group-enrollments", 200, "sync again", coord)
    c.expect(again.get("created") == 0, f"sync is idempotent: {again}")
    return {"offering": offering["id"], "course": course["id"], "p1": p1["id"], "p2": p2["id"], "foreign_period": foreign_period["id"]}


async def check_grades(c: Checker, h: dict[str, dict], ctx: dict, quiz_id: int) -> dict[str, int]:
    prof, offering = h["prof"], ctx["offering"]
    mine = await c.call("GET", "/assessment/teaching/offerings", 200, "teaching offerings", prof)
    c.expect([o["id"] for o in mine] == [offering], f"instructor sees own offerings: {mine}")
    others = await c.call("GET", "/assessment/teaching/offerings", 200, "other instructor offerings", h["outro"])
    c.expect(others == [], f"other instructor sees none: {others}")
    await c.call("GET", f"/assessment/offerings/{offering}/items", 403, "other instructor blocked", h["outro"])
    await c.call("GET", f"/assessment/offerings/{offering}/gradebook", 403, "student blocked", h["ana"])

    items_path = f"/assessment/offerings/{offering}/items"
    prova = await c.call("POST", items_path, 201, "item prova", prof, json={"name": "Prova 1", "grading_period_id": ctx["p1"], "weight": 2})
    trabalho = await c.call("POST", items_path, 201, "item trabalho", prof,
                            json={"name": "Trabalho", "kind": "assignment", "grading_period_id": ctx["p1"], "max_score": 5})
    quiz = await c.call("POST", items_path, 201, "item quiz", prof,
                        json={"name": "Quiz", "kind": "quiz", "grading_period_id": ctx["p2"], "quiz_id": quiz_id})
    await c.call("POST", items_path, 400, "period from another term", prof, json={"name": "X", "grading_period_id": ctx["foreign_period"]})

    rows = await c.call("GET", f"/assessment/items/{prova['id']}/grades", 200, "grade rows", prof)
    enrollment = {row["student"]["name"]: row["class_enrollment_id"] for row in rows}
    c.expect(set(enrollment) == {"Ana", "Bia"}, f"grade rows list active students: {rows}")
    await c.call("PUT", f"/assessment/items/{prova['id']}/grades", 200, "save prova", prof,
                 json=[{"class_enrollment_id": enrollment["Ana"], "score": 8}, {"class_enrollment_id": enrollment["Bia"], "score": 5}])
    await c.call("PUT", f"/assessment/items/{trabalho['id']}/grades", 200, "save trabalho", prof,
                 json=[{"class_enrollment_id": enrollment["Ana"], "score": 4}, {"class_enrollment_id": enrollment["Bia"], "score": 2.5}])
    await c.call("PUT", f"/assessment/items/{trabalho['id']}/grades", 400, "score above max", prof,
                 json=[{"class_enrollment_id": enrollment["Ana"], "score": 6}])
    await c.call("PUT", f"/assessment/items/{trabalho['id']}/grades", 400, "enrollment from elsewhere", prof,
                 json=[{"class_enrollment_id": MISSING_ID, "score": 1}])
    await c.call("PATCH", f"/assessment/items/{trabalho['id']}", 400, "max below existing scores", prof, json={"max_score": 3})

    imported = await c.call("POST", f"/assessment/items/{quiz['id']}/import-quiz", 200, "import quiz", prof)
    c.expect(imported == {"imported": 1, "without_attempt": 1}, f"quiz import counts: {imported}")
    await c.call("POST", f"/assessment/items/{prova['id']}/import-quiz", 400, "import on non-quiz item", prof)

    book = await c.call("GET", f"/assessment/offerings/{offering}/gradebook", 200, "gradebook", prof)
    by_name = {row["student"]["name"]: row for row in book["rows"]}
    ana, bia = by_name["Ana"], by_name["Bia"]
    c.expect(book["scheme"]["name"] == "Conceitos", f"default scheme applied: {book['scheme']['name']}")
    c.expect(ana["scores"][str(quiz["id"])] == 9, f"quiz best attempt as 9/10: {ana['scores']}")
    c.expect(ana["period_averages"] == {str(ctx["p1"]): 8.0, str(ctx["p2"]): 9.0}, f"ana period averages: {ana['period_averages']}")
    c.expect(ana["average"] == 8.5 and ana["concept"] == "B", f"ana overall: {ana['average']} {ana['concept']}")
    c.expect(bia["period_averages"] == {str(ctx["p1"]): 5.0, str(ctx["p2"]): None}, f"bia periods (pending quiz): {bia['period_averages']}")
    c.expect(bia["average"] == 5.0 and bia["concept"] == "C", f"bia overall: {bia['average']} {bia['concept']}")
    return {"prova": prova["id"], "quiz": quiz["id"], "ana": enrollment["Ana"], "bia": enrollment["Bia"]}


async def check_diary(c: Checker, h: dict[str, dict], ctx: dict, grades: dict[str, int], meeting_id: int) -> None:
    prof, coord, offering = h["prof"], h["coord"], ctx["offering"]
    diary = f"/assessment/offerings/{offering}/diary"
    first = await c.call("POST", diary, 201, "diary entry 1", prof, json={"date": "2027-03-10", "lesson_count": 2, "content_taught": "Frações"})
    await c.call("POST", diary, 409, "same date twice", prof, json={"date": "2027-03-10", "content_taught": "x"})
    await c.call("POST", diary, 400, "date outside term", prof, json={"date": "2029-01-10", "content_taught": "x"})
    second = await c.call("POST", diary, 201, "diary entry from meeting", prof,
                          json={"date": "2027-03-12", "lesson_count": 2, "content_taught": "Decimais", "scheduled_meeting_id": meeting_id})

    prefilled = await c.call("GET", f"/assessment/diary-entries/{second['id']}/attendance", 200, "attendance prefilled", prof)
    absences = {row["student"]["name"]: row["absences"] for row in prefilled}
    c.expect(absences == {"Ana": 2, "Bia": 0}, f"meeting absence prefills diary: {absences}")
    await c.call("PUT", f"/assessment/diary-entries/{second['id']}/attendance", 200, "confirm meeting attendance", prof,
                 json=[{"class_enrollment_id": grades["ana"], "absences": 2, "justified": True, "note": "Atestado"}])
    await c.call("PUT", f"/assessment/diary-entries/{first['id']}/attendance", 200, "attendance entry 1", prof,
                 json=[{"class_enrollment_id": grades["bia"], "absences": 2}])
    await c.call("PUT", f"/assessment/diary-entries/{first['id']}/attendance", 400, "absences above lessons", prof,
                 json=[{"class_enrollment_id": grades["bia"], "absences": 3}])
    await c.call("PATCH", f"/assessment/diary-entries/{first['id']}", 400, "lesson count below absences", prof, json={"lesson_count": 1})

    book = await c.call("GET", f"/assessment/offerings/{offering}/gradebook", 200, "gradebook with attendance", prof)
    rates = {row["student"]["name"]: (row["absences"], row["attendance_rate"]) for row in book["rows"]}
    c.expect(book["total_lessons"] == 4, f"total lessons: {book['total_lessons']}")
    c.expect(rates == {"Ana": (0, 100.0), "Bia": (2, 50.0)}, f"justified absences do not count: {rates}")

    # Encerrar o 1o bimestre bloqueia notas e diario daquele intervalo; o 2o segue aberto.
    await c.call("POST", f"/academic/grading-periods/{ctx['p1']}/status", 200, "close period 1", coord, json={"status": "closed"})
    await c.call("PUT", f"/assessment/items/{grades['prova']}/grades", 409, "grades locked", prof,
                 json=[{"class_enrollment_id": grades["ana"], "score": 10}])
    await c.call("POST", f"/assessment/offerings/{offering}/items", 409, "no new item in closed period", prof,
                 json={"name": "Extra", "grading_period_id": ctx["p1"]})
    await c.call("PATCH", f"/assessment/diary-entries/{first['id']}", 409, "diary locked", prof, json={"content_taught": "x"})
    entries = await c.call("GET", diary, 200, "list diary", prof)
    c.expect(all(entry["locked"] for entry in entries), f"entries flagged locked: {entries}")
    await c.call("POST", diary, 201, "diary in open period", prof, json={"date": "2027-05-10", "content_taught": "Porcentagem"})
    await c.call("PUT", f"/assessment/items/{grades['quiz']}/grades", 200, "open period still editable", prof,
                 json=[{"class_enrollment_id": grades["bia"], "score": 7}])
    return first["id"]


def check_result_rules(c: Checker) -> None:
    scheme = GradingSchemeOut(id=None, name="t", scale="numeric", min_value=0, max_value=10, passing_grade=6, formula="weighted",
                              recovery_enabled=True, min_attendance=75, concepts=[], is_default=False)
    cases = [
        ((7, None, 90), (7, "approved")),
        ((4, None, 90), (4, "recovery")),
        ((4, 7, 90), (7, "approved")),
        ((4, 5, 90), (5, "failed")),
        ((8, None, 60), (8, "failed_attendance")),
        ((None, None, None), (None, "in_progress")),
    ]
    for args, (grade, result) in cases:
        outcome = decide(*args, scheme)
        c.expect((outcome.final_grade, outcome.result.value) == (grade, result), f"decide{args} -> {outcome}")
    no_recovery = scheme.model_copy(update={"recovery_enabled": False})
    c.expect(decide(4, None, 90, no_recovery).result.value == "failed", "without recovery a low grade fails directly")


async def check_results(c: Checker, h: dict[str, dict], ctx: dict, grades: dict[str, int], first_entry: int) -> None:
    prof, coord, offering = h["prof"], h["coord"], ctx["offering"]
    base = f"/assessment/offerings/{offering}"
    await c.call("POST", f"{base}/results/compute", 409, "results need all periods closed", prof)

    # Coordenacao reabre o 1o bimestre para justificar as faltas de Bia e encerra de novo.
    await c.call("POST", f"/academic/grading-periods/{ctx['p1']}/status", 200, "reopen period 1", coord, json={"status": "open"})
    await c.call("PUT", f"/assessment/diary-entries/{first_entry}/attendance", 200, "justify bia", prof,
                 json=[{"class_enrollment_id": grades["bia"], "absences": 2, "justified": True}])
    await c.call("POST", f"/academic/grading-periods/{ctx['p1']}/status", 200, "close period 1 again", coord, json={"status": "closed"})
    await c.call("PUT", f"/assessment/items/{grades['quiz']}/grades", 200, "bia low quiz", prof,
                 json=[{"class_enrollment_id": grades["bia"], "score": 3}])

    closed = await c.call("POST", f"{base}/periods/{ctx['p2']}/close", 200, "close period 2 in offering", prof)
    c.expect(closed.get("closed_students") == 2, f"closure consolidates both students: {closed}")
    await c.call("POST", f"{base}/periods/{ctx['p2']}/close", 409, "period already closed", prof)
    await c.call("PUT", f"/assessment/items/{grades['quiz']}/grades", 409, "closed in offering locks grades", prof,
                 json=[{"class_enrollment_id": grades["bia"], "score": 9}])
    await c.call("DELETE", f"{base}/periods/{ctx['p2']}/close", 403, "instructor cannot reopen", prof)

    results = await c.call("POST", f"{base}/results/compute", 200, "compute results", prof)
    rows = {row["student"]["name"]: row for row in results["rows"]}
    c.expect(results["pending_period_ids"] == [], f"no pending periods: {results['pending_period_ids']}")
    c.expect((rows["Ana"]["final_grade"], rows["Ana"]["result"]) == (8.5, "approved"), f"ana approved: {rows['Ana']}")
    c.expect((rows["Bia"]["final_grade"], rows["Bia"]["result"], rows["Bia"]["attendance_rate"]) == (4.0, "recovery", 100.0), f"bia in recovery: {rows['Bia']}")
    c.expect([p["average"] for p in rows["Bia"]["periods"]] == [5.0, 3.0], f"bia period results: {rows['Bia']['periods']}")

    await c.call("POST", f"{base}/finalize", 403, "instructor cannot finalize", prof)
    await c.call("POST", f"{base}/finalize", 409, "pending recovery blocks finalization", coord)
    card = await c.call("GET", "/assessment/my/report-card", 200, "report card before finalization", h["ana"])
    c.expect(len(card) == 1 and card[0]["result"] == "in_progress" and len(card[0]["periods"]) == 2, f"closed periods visible, result hidden: {card}")

    recovery = f"{base}/recovery"
    await c.call("PUT", recovery, 400, "approved student has no recovery", prof, json=[{"class_enrollment_id": grades["ana"], "score": 9}])
    await c.call("PUT", recovery, 400, "recovery above scale", prof, json=[{"class_enrollment_id": grades["bia"], "score": 11}])
    after = await c.call("PUT", recovery, 200, "bia recovery", prof, json=[{"class_enrollment_id": grades["bia"], "score": 7}])
    bia = next(row for row in after["rows"] if row["student"]["name"] == "Bia")
    c.expect((bia["final_grade"], bia["result"], bia["recovery_score"]) == (7.0, "approved", 7.0), f"recovery replaces lower grade: {bia}")

    final = await c.call("POST", f"{base}/finalize", 200, "finalize", coord)
    c.expect(final.get("finalized") is True, f"offering finalized: {final.get('finalized')}")
    await c.call("PUT", recovery, 409, "no recovery after finalization", prof, json=[{"class_enrollment_id": grades["bia"], "score": 8}])
    await c.call("POST", f"{base}/diary", 409, "diary locked after finalization", prof, json={"date": "2027-06-01", "content_taught": "x"})
    await c.call("POST", f"{base}/results/compute", 409, "compute locked after finalization", prof)
    await c.call("DELETE", f"{base}/periods/{ctx['p2']}/close", 409, "no reopen after finalization", coord)

    card = await c.call("GET", "/assessment/my/report-card", 200, "report card after finalization", h["ana"])
    c.expect((card[0]["finalized"], card[0]["final_grade"], card[0]["result"]) == (True, 8.5, "approved"), f"published result: {card}")
    results = await c.call("GET", f"{base}/results", 200, "results after finalization", prof)
    c.expect(len(results["rows"]) == 2, f"completed enrollments still listed: {len(results['rows'])}")
    with SessionLocal() as db:
        published = db.query(NotificationEvent).filter(NotificationEvent.event_type == NotificationEventType.grades_published).count()
    c.expect(published == 2, f"one grades_published notification per student: {published}")


async def run() -> int:
    institution_id, ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(name) for name, _ in USERS}
        ctx = await setup_structure(c, h, ids)
        quiz_id, meeting_id = seed_quiz_and_meeting(institution_id, ctx["course"], ctx["offering"], ids)
        grades = await check_grades(c, h, ctx, quiz_id)
        first_entry = await check_diary(c, h, ctx, grades, meeting_id)
        check_result_rules(c)
        await check_results(c, h, ctx, grades, first_entry)

    if c.failures:
        print("Assessment flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Assessment flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
