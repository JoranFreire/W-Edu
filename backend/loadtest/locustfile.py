"""Teste de carga do W-Edu com Locust.

Simula alunos e administradores de varias instituicoes usando os dados de
loadtest/seed.json. Veja loadtest/README.md.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from locust import HttpUser, between, events, task

SEED_FILE = Path(__file__).with_name("seed.json")
SEED: dict = {}


@events.init.add_listener
def load_seed(environment, **_kwargs) -> None:
    if not SEED_FILE.exists():
        raise SystemExit(f"{SEED_FILE} nao encontrado. Rode antes: python loadtest/seed.py")
    SEED.update(json.loads(SEED_FILE.read_text()))


class InstitutionUser(HttpUser):
    abstract = True
    wait_time = between(1, 3)

    def login(self, email: str) -> None:
        self.institution = self.institution or random.choice(SEED["institutions"])
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": SEED["password"], "institution": self.institution["slug"]},
            name="/auth/login",
        )
        response.raise_for_status()
        self.client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"

    def random_course(self) -> int:
        return random.choice(self.institution["courses"])

    def random_lesson(self, course_id: int | None = None) -> int:
        course_id = course_id or self.random_course()
        return random.choice(self.institution["lessons"][str(course_id)])


class StudentUser(InstitutionUser):
    weight = 9

    def on_start(self) -> None:
        self.institution = random.choice(SEED["institutions"])
        self.login(random.choice(self.institution["students"]))

    @task(5)
    def list_courses(self) -> None:
        self.client.get("/courses", name="/courses")

    @task(4)
    def list_lessons(self) -> None:
        self.client.get(f"/lessons/course/{self.random_course()}", name="/lessons/course/[id]")

    @task(3)
    def read_lesson(self) -> None:
        self.client.get(f"/lessons/{self.random_lesson()}", name="/lessons/[id]")

    @task(3)
    def course_progress(self) -> None:
        self.client.get("/progress/me/courses", name="/progress/me/courses")

    @task(2)
    def consume_lesson(self) -> None:
        self.client.post(f"/progress/consume/{self.random_lesson()}", name="/progress/consume/[id]")

    @task(1)
    def check_in(self) -> None:
        self.client.post(f"/schedule/check-in/{self.institution['checkin_token']}", name="/schedule/check-in/[token]")

    @task(1)
    def my_certificates(self) -> None:
        self.client.get("/certificates/students/me", name="/certificates/students/me")


class AdminUser(InstitutionUser):
    weight = 1

    def on_start(self) -> None:
        self.institution = random.choice(SEED["institutions"])
        self.login(self.institution["admin"])

    @task(3)
    def list_users(self) -> None:
        self.client.get("/admin/users", name="/admin/users")

    @task(2)
    def list_classes(self) -> None:
        self.client.get("/schedule/classes", name="/schedule/classes")

    @task(2)
    def class_enrollments(self) -> None:
        self.client.get(f"/schedule/classes/{self.institution['class_id']}/enrollments", name="/schedule/classes/[id]/enrollments")

    @task(2)
    def attendance_report(self) -> None:
        self.client.get(
            f"/schedule/meetings/{self.institution['meeting_id']}/attendance-report",
            name="/schedule/meetings/[id]/attendance-report",
        )

    @task(1)
    def course_enrollments(self) -> None:
        self.client.get(f"/enrollments/course/{self.random_course()}", name="/enrollments/course/[id]")
