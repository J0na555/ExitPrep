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

# Workaround: Import question.py before __init__.py imports question_model
# We temporarily prevent question_model from being imported by mocking it in sys.modules
import sys
import types

# Create a dummy module for question_model to prevent the real one from loading
dummy_question_model = types.ModuleType("app.models.question_model")
sys.modules["app.models.question_model"] = dummy_question_model

# Now import question.py - it will register the questions table
from app.models.question import Question, QuestionDifficulty, QuestionSource

# Remove the dummy so other imports work normally
del sys.modules["app.models.question_model"]

# Import other models normally
from app.models.course_model import Course
from app.models.option import Option


def _locate_async_session_maker() -> Any:
    """Try to find the async session maker object in app.utils.database.

    The project may name the variable differently (e.g. `async_session_maker`,
    `AsyncSessionLocal`). We try a few common names and raise if none found.
    """
    dbmod = import_module("app.utils.database")
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

                question = Question(
                    course_id=course.id,
                    question_text=question_text,
                    difficulty=QuestionDifficulty.medium,
                    source=QuestionSource.generated,
                )
                session.add(question)
                for opt in options:
                    option = Option(option_text=opt["text"], is_correct=opt["is_correct"])
                    question.options.append(option)

                await session.flush()

                correct_opt = next((o for o in question.options if o.is_correct), None)
                if correct_opt is not None:
                    question.correct_option_id = correct_opt.id

                print(f"  Inserted question: '{question_text[:60]}' (course: {course.title})")



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
