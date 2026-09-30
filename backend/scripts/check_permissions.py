"""Validate critical route permission dependencies.

This is a lightweight guard for the role matrix in docs/PERMISSIONS.md. It does
not replace endpoint tests, but it catches accidental dependency regressions on
the routes where role boundaries matter most.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.routing import APIRoute

from main import app


ExpectedRoute = tuple[str, str, str]


EXPECTED: list[ExpectedRoute] = [
    ("POST", "/courses", "get_current_admin_or_coordinator"),
    ("PATCH", "/courses/{course_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/courses/{course_id}", "get_current_admin"),
    ("POST", "/courses/{course_id}/modules", "get_current_admin_or_coordinator"),
    ("PATCH", "/courses/modules/{module_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/courses/modules/{module_id}", "get_current_admin"),
    ("POST", "/courses/{course_id}/prerequisites", "get_current_admin_or_coordinator"),
    ("DELETE", "/courses/{course_id}/prerequisites/{prerequisite_course_id}", "get_current_admin"),
    ("POST", "/learning-paths", "get_current_admin_or_coordinator"),
    ("PATCH", "/learning-paths/{path_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/learning-paths/{path_id}", "get_current_admin"),
    ("POST", "/learning-paths/{path_id}/courses", "get_current_admin_or_coordinator"),
    ("DELETE", "/learning-paths/{path_id}/courses/{course_id}", "get_current_admin"),
    ("POST", "/lessons", "get_current_admin_or_coordinator"),
    ("PATCH", "/lessons/{lesson_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/lessons/{lesson_id}", "get_current_admin"),
    ("GET", "/assignments/lessons/{lesson_id}/submissions", "get_current_admin_or_coordinator"),
    ("PATCH", "/assignments/submissions/{submission_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/admin/users/{student_id}", "get_current_admin"),
    ("POST", "/admin/quizzes", "get_current_admin_or_coordinator"),
    ("PATCH", "/admin/quizzes/lesson/{lesson_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/admin/quizzes/lesson/{lesson_id}", "get_current_admin"),
    ("POST", "/admin/quizzes/lesson/{lesson_id}/questions", "get_current_admin_or_coordinator"),
    ("PATCH", "/admin/quiz-questions/{question_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/admin/quiz-questions/{question_id}", "get_current_admin"),
    ("PATCH", "/admin/users/availability/{availability_id}", "get_current_academic_staff"),
    ("DELETE", "/admin/users/availability/{availability_id}", "get_current_academic_staff"),
    ("PATCH", "/certificates/rules/{course_id}", "get_current_admin_or_coordinator"),
    ("POST", "/certificates/courses/{course_id}/students/{student_id}/issue", "get_current_admin_or_coordinator"),
    ("POST", "/certificates/{certificate_id}/revoke", "get_current_admin"),
    ("GET", "/certificates/{certificate_id}/download", "get_current_student"),
    ("POST", "/schedule/classes", "get_current_admin_or_coordinator"),
    ("PATCH", "/schedule/classes/{class_id}", "get_current_admin_or_coordinator"),
    ("POST", "/schedule/meetings", "get_current_admin_or_coordinator"),
    ("POST", "/schedule/meetings/{meeting_id}/attendance", "get_current_admin_or_coordinator"),
    ("POST", "/schedule/meetings/{meeting_id}/practical-assessments", "get_current_admin_or_coordinator"),
    ("GET", "/schedule/meetings/{meeting_id}/attendance-report", "get_current_admin_or_coordinator"),
    ("POST", "/notifications/events/process-due", "get_current_admin_or_coordinator"),
    ("GET", "/finance/subscriptions", "get_current_admin_or_company_manager"),
    ("POST", "/finance/charges/{charge_id}/gateway/asaas", "get_current_admin"),
    ("GET", "/analytics/overview", "get_current_admin_or_company_manager"),
    ("POST", "/academic/units", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/units/{unit_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/units/{unit_id}", "get_current_admin"),
    ("POST", "/academic/programs", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/programs/{program_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/programs/{program_id}", "get_current_admin"),
    ("POST", "/academic/subjects", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/subjects/{subject_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/subjects/{subject_id}", "get_current_admin"),
    ("POST", "/academic/subjects/{subject_id}/prerequisites", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/subjects/{subject_id}/prerequisites/{required_subject_id}", "get_current_admin"),
    ("POST", "/academic/subjects/{subject_id}/equivalences", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/subjects/{subject_id}/equivalences/{equivalent_subject_id}", "get_current_admin"),
    ("POST", "/academic/programs/{program_id}/curricula", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/curricula/{curriculum_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/curricula/{curriculum_id}", "get_current_admin"),
    ("POST", "/academic/curricula/{curriculum_id}/activate", "get_current_admin_or_coordinator"),
    ("POST", "/academic/curricula/{curriculum_id}/archive", "get_current_admin_or_coordinator"),
    ("POST", "/academic/curricula/{curriculum_id}/versions", "get_current_admin_or_coordinator"),
    ("POST", "/academic/curricula/{curriculum_id}/components", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/curriculum-components/{component_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/curriculum-components/{component_id}", "get_current_admin_or_coordinator"),
    ("GET", "/academic/curricula/{curriculum_id}", "get_current_student"),
    ("POST", "/academic/terms", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/terms/{term_id}", "get_current_admin_or_coordinator"),
    ("POST", "/academic/terms/{term_id}/status", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/terms/{term_id}", "get_current_admin"),
    ("POST", "/academic/terms/{term_id}/grading-periods", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/grading-periods/{period_id}", "get_current_admin_or_coordinator"),
    ("POST", "/academic/grading-periods/{period_id}/status", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/grading-periods/{period_id}", "get_current_admin"),
    ("POST", "/academic/calendar-events", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/calendar-events/{event_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/calendar-events/{event_id}", "get_current_admin_or_coordinator"),
    ("GET", "/academic/program-enrollments", "get_current_admin_or_coordinator"),
    ("GET", "/academic/program-enrollments/me", "get_current_student"),
    ("POST", "/academic/program-enrollments", "get_current_admin_or_coordinator"),
    ("POST", "/academic/program-enrollments/{enrollment_id}/status", "get_current_admin_or_coordinator"),
    ("POST", "/academic/class-groups", "get_current_admin_or_coordinator"),
    ("PATCH", "/academic/class-groups/{group_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/class-groups/{group_id}", "get_current_admin"),
    ("GET", "/academic/class-groups/{group_id}/members", "get_current_admin_or_coordinator"),
    ("POST", "/academic/class-groups/{group_id}/members", "get_current_admin_or_coordinator"),
    ("DELETE", "/academic/class-groups/{group_id}/members/{enrollment_id}", "get_current_admin_or_coordinator"),
    ("POST", "/assessment/grading-schemes", "get_current_admin_or_coordinator"),
    ("PATCH", "/assessment/grading-schemes/{scheme_id}", "get_current_admin_or_coordinator"),
    ("DELETE", "/assessment/grading-schemes/{scheme_id}", "get_current_admin"),
    ("GET", "/assessment/teaching/offerings", "get_current_teaching_staff"),
    ("GET", "/assessment/offerings/{offering_id}", "get_current_teaching_staff"),
    ("POST", "/assessment/offerings/{offering_id}/sync-group-enrollments", "get_current_admin_or_coordinator"),
    ("GET", "/assessment/offerings/{offering_id}/items", "get_current_teaching_staff"),
    ("POST", "/assessment/offerings/{offering_id}/items", "get_current_teaching_staff"),
    ("PATCH", "/assessment/items/{item_id}", "get_current_teaching_staff"),
    ("DELETE", "/assessment/items/{item_id}", "get_current_teaching_staff"),
    ("GET", "/assessment/items/{item_id}/grades", "get_current_teaching_staff"),
    ("PUT", "/assessment/items/{item_id}/grades", "get_current_teaching_staff"),
    ("POST", "/assessment/items/{item_id}/import-quiz", "get_current_teaching_staff"),
    ("GET", "/assessment/offerings/{offering_id}/gradebook", "get_current_teaching_staff"),
    ("GET", "/assessment/offerings/{offering_id}/diary", "get_current_teaching_staff"),
    ("POST", "/assessment/offerings/{offering_id}/diary", "get_current_teaching_staff"),
    ("PATCH", "/assessment/diary-entries/{entry_id}", "get_current_teaching_staff"),
    ("DELETE", "/assessment/diary-entries/{entry_id}", "get_current_teaching_staff"),
    ("GET", "/assessment/diary-entries/{entry_id}/attendance", "get_current_teaching_staff"),
    ("PUT", "/assessment/diary-entries/{entry_id}/attendance", "get_current_teaching_staff"),
    ("POST", "/assessment/offerings/{offering_id}/periods/{period_id}/close", "get_current_teaching_staff"),
    ("DELETE", "/assessment/offerings/{offering_id}/periods/{period_id}/close", "get_current_admin_or_coordinator"),
    ("GET", "/assessment/offerings/{offering_id}/results", "get_current_teaching_staff"),
    ("POST", "/assessment/offerings/{offering_id}/results/compute", "get_current_teaching_staff"),
    ("PUT", "/assessment/offerings/{offering_id}/recovery", "get_current_teaching_staff"),
    ("POST", "/assessment/offerings/{offering_id}/finalize", "get_current_admin_or_coordinator"),
    ("GET", "/assessment/my/report-card", "get_current_student"),
]


def dependency_names(route: APIRoute) -> set[str]:
    return {dependency.call.__name__ for dependency in route.dependant.dependencies if dependency.call}


def iter_matching_routes(method: str, path: str) -> Iterable[APIRoute]:
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path == path and method in route.methods:
            yield route


def main() -> int:
    failures: list[str] = []
    for method, path, expected_dependency in EXPECTED:
        routes = list(iter_matching_routes(method, path))
        if not routes:
            failures.append(f"{method} {path}: route not found")
            continue
        for route in routes:
            names = dependency_names(route)
            if expected_dependency not in names:
                failures.append(
                    f"{method} {path}: expected {expected_dependency}, got {', '.join(sorted(names)) or 'none'}"
                )

    if failures:
        print("Permission check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Permission check passed for {len(EXPECTED)} route expectations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
