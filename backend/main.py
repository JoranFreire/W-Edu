import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import assignments, auth, users, students, courses, lessons, enrollments, progress, sessions, webhooks, admin, quiz, learning_paths, schedule, certificates, notifications, finance, documents, analytics, forum, chat, institutions, platform, academic, assessment, secretariat, guardians, school_life, registration, completion, tuition, contracts, saas, admissions
from app.services.notification_worker import run_notification_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()
    worker_task: asyncio.Task | None = None
    if settings.NOTIFICATION_WORKER_ENABLED:
        worker_task = asyncio.create_task(run_notification_worker(stop_event))
    try:
        yield
    finally:
        stop_event.set()
        if worker_task:
            worker_task.cancel()
            with suppress(asyncio.CancelledError):
                await worker_task


app = FastAPI(title="W-Edu API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])
app.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
app.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
app.include_router(progress.router, prefix="/progress", tags=["progress"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(quiz.router, prefix="/quizzes", tags=["quizzes"])
app.include_router(learning_paths.router, prefix="/learning-paths", tags=["learning-paths"])
app.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
app.include_router(certificates.router, prefix="/certificates", tags=["certificates"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(finance.router, prefix="/finance", tags=["finance"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(forum.router, prefix="/forum", tags=["forum"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(institutions.router, prefix="/institutions", tags=["institutions"])
app.include_router(platform.router, prefix="/platform", tags=["platform"])
app.include_router(academic.router, prefix="/academic", tags=["academic"])
app.include_router(assessment.router, prefix="/assessment", tags=["assessment"])
app.include_router(secretariat.router, prefix="/secretariat", tags=["secretariat"])
app.include_router(guardians.router, prefix="/guardians", tags=["guardians"])
app.include_router(school_life.router, prefix="/school", tags=["school"])
app.include_router(registration.router, prefix="/registration", tags=["registration"])
app.include_router(completion.router, prefix="/completion", tags=["completion"])
app.include_router(tuition.router, prefix="/tuition", tags=["tuition"])
app.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
app.include_router(saas.router, prefix="/saas", tags=["saas"])
app.include_router(admissions.router, prefix="/admissions", tags=["admissions"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "w-edu"}
