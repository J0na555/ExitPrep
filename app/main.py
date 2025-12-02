from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth as auth_router
from app.routers import user as user_router
from app.routers import course_router, chapter_router, question_router


app = FastAPI(title="ExitPrep Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(course_router.router, prefix="/api/courses")
app.include_router(chapter_router.router, prefix="/api/chapters")
app.include_router(question_router.router, prefix="/api/questions")

@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


__all__ = ["app"]


