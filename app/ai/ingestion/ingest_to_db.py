"""Ingest processed question JSON files into the database.

This script looks for JSON files in `backend/app/ai/data/processed_questions/`,
validates their shape, and inserts Course, Question and Option records into
the application's database using the project's async session maker and
SQLAlchemy models.

Usage:
    python ingest_to_db.py

Notes:
    - The script uses the session maker defined in `app.utils.database`.
      It will try to locate an attribute named `async_session_maker` and
      fall back to common alternatives (e.g. `AsyncSessionLocal`).
    - Questions are considered duplicates when a Question with the same
      `question_text` already exists; those are skipped.
"""

from __future__ import annotations

import asyncio
import json
import sys
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import select


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
from app.utils.config import settings, get_settings

# Load environment variables from .env file in the project root
dotenv_path = REPO_ROOT / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Override the DB_HOST to connect from outside Docker
# The script runs on the host, but the DB is in a container. We connect via localhost.
settings.DB_HOST = "localhost"
# Re-initialize settings to reconstruct DATABASE_URL with the new host
get_settings.cache_clear()
settings = get_settings()

# Now that environment is loaded and patched, import application modules
from app.models.question_model import Question, QuestionDifficulty
from app.models.course_model import Course
from app.models.chapter_model import Chapter
from app.models.option import Option


def _locate_async_session_maker() -> Any:
    """Try to find the async session maker object in app.database.

    The project may name the variable differently (e.g. `async_session_maker`,
    `AsyncSessionLocal`). We try a few common names and raise if none found.
    """
    dbmod = import_module("app.database")
    for name in ("async_session_maker", "AsyncSessionLocal", "async_sessionmaker", "AsyncSessionMaker"):
        maker = getattr(dbmod, name, None)
        if maker is not None:
            return maker
    raise ImportError(
        "Could not find async session maker in app.utils.database. "
        "Expected attribute like 'async_session_maker' or 'AsyncSessionLocal'."
    )


async def load_json_file(path: Path) -> List[Dict[str, Any]]:
    """Asynchronously load and parse a JSON file, returning the list of questions.

    Uses asyncio.to_thread to perform blocking IO on a thread pool.
    """
    def _read() -> List[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    data = await asyncio.to_thread(_read)
    return data


async def get_or_create_course(session: Any, course_name: str) -> Course:
    """Retrieve a Course by title, creating it if it doesn't exist.

    Returns the Course instance (may be newly added but not necessarily committed).
    """
    result = await session.execute(select(Course).where(Course.title == course_name))
    course = result.scalar_one_or_none()
    if course:
        return course

    course = Course(title=course_name)
    session.add(course)
    await session.flush()
    return course


async def get_or_create_default_chapter(session: Any, course: Course, title: str = "Imported") -> Chapter:
    """Ensure a chapter exists for the given course and return it."""
    result = await session.execute(select(Chapter).where(Chapter.course_id == course.id, Chapter.title == title))
    chapter = result.scalar_one_or_none()
    if chapter:
        return chapter

    chapter = Chapter(course_id=course.id, title=title)
    session.add(chapter)
    await session.flush()
    return chapter


def _validate_question_item(item: Dict[str, Any]) -> None:
    """Validate structure of a question item; raise ValueError on invalid data."""
    if not isinstance(item, dict):
        raise ValueError("Question item is not an object/dict")

    if "course_name" not in item or not isinstance(item["course_name"], str):
        raise ValueError("Missing or invalid 'course_name'")

    if "question_text" not in item or not isinstance(item["question_text"], str):
        raise ValueError("Missing or invalid 'question_text'")

    if "options" not in item or not isinstance(item["options"], list):
        raise ValueError("Missing or invalid 'options' (must be a list)")

    for opt in item["options"]:
        if not isinstance(opt, dict):
            raise ValueError("Each option must be an object/dict")
        if "text" not in opt or not isinstance(opt["text"], str):
            raise ValueError("Option missing 'text' or it is not a string")
        if "is_correct" not in opt or not isinstance(opt["is_correct"], bool):
            raise ValueError("Option missing 'is_correct' or it is not a boolean")


async def process_file(path: Path, async_session_maker: Any) -> None:
    """Process a single JSON file: validate and insert questions into DB."""
    print(f"Processing file: {path}")
    try:
        data = await load_json_file(path)
    except Exception as exc:
        print(f"  Failed to read JSON: {exc}")
        return

    if not isinstance(data, list):
        print(f"  Skipping {path.name}: top-level JSON must be a list of questions")
        return

    async with async_session_maker() as session:
        async with session.begin():
            for idx, item in enumerate(data, start=1):
                try:
                    _validate_question_item(item)
                except ValueError as ve:
                    print(f"  Skipping item #{idx}: validation error: {ve}")
                    continue

                course_name = item["course_name"].strip()
                question_text = item["question_text"].strip()
                options = item["options"]

                existing = await session.execute(
                    select(Question).where(Question.question_text == question_text)
                )
                existing_q = existing.scalar_one_or_none()
                if existing_q:
                    print(f"  Skipped existing question: '{question_text[:60]}'")
                    continue

                course = await get_or_create_course(session, course_name)
                chapter = await get_or_create_default_chapter(session, course)

                # Determine correct answer (if any)
                correct_answer = None
                for opt in options:
                    if opt.get("is_correct"):
                        correct_answer = opt.get("text")
                        break

                question = Question(
                    chapter_id=chapter.id,
                    question_text=question_text,
                    options=options,
                    correct_answer=correct_answer or (options[0].get("text") if options else ""),
                    difficulty=QuestionDifficulty.medium,
                    explanation=None,
                )
                session.add(question)
                await session.flush()

                print(f"  Inserted question: '{question_text[:60]}' (course: {course.name}, chapter: {chapter.title})")



async def main() -> None:
    """Main entry point: find JSON files and process them sequentially."""
    ai_dir = Path(__file__).resolve().parents[1]
    input_dir = ai_dir / "data" / "processed_questions"

    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return

    async_session_maker = _locate_async_session_maker()

    json_files = sorted(input_dir.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in: {input_dir}")
        return

    for path in json_files:
        try:
            await process_file(path, async_session_maker)
        except Exception as exc: 
            print(f"Error processing {path.name}: {exc}")

    print("Ingestion complete")


if __name__ == "__main__":
    asyncio.run(main())
