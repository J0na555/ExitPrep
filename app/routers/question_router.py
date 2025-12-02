from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chapter_model import Chapter
from app.models.question_model import Question
from app.models.user import User
from app.schemas.question_schema import QuestionCreate, QuestionRead, QuestionUpdate
from app.utils.database import get_db
from app.utils.dependencies import get_current_user

router = APIRouter(tags=["questions"])


@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionRead:
    """Create a new question inside a chapter."""
    # Verify chapter exists
    result = await db.execute(select(Chapter).where(Chapter.id == question_data.chapter_id))
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )
    
    db_question = Question(
        chapter_id=question_data.chapter_id,
        question_text=question_data.question_text,
        options=question_data.options,
        correct_answer=question_data.correct_answer,
        difficulty=question_data.difficulty,
        explanation=question_data.explanation,
    )
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return QuestionRead.model_validate(db_question)


@router.get("/chapter/{chapter_id}", response_model=List[QuestionRead])
async def get_questions_by_chapter_id(
    chapter_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[QuestionRead]:
    """Get all questions for a specific chapter."""
    # Verify chapter exists
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )
    
    result = await db.execute(
        select(Question).where(Question.chapter_id == chapter_id)
    )
    questions = result.scalars().all()
    return [QuestionRead.model_validate(question) for question in questions]


@router.get("/{question_id}", response_model=QuestionRead)
async def get_question_by_id(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionRead:
    """Get a question by ID."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    
    return QuestionRead.model_validate(question)


@router.put("/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: uuid.UUID,
    question_data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionRead:
    """Update a question."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    
    # Verify chapter exists if chapter_id is being updated
    if question_data.chapter_id is not None:
        chapter_result = await db.execute(
            select(Chapter).where(Chapter.id == question_data.chapter_id)
        )
        chapter = chapter_result.scalar_one_or_none()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found",
            )
        question.chapter_id = question_data.chapter_id
    
    # Update fields if provided
    if question_data.question_text is not None:
        question.question_text = question_data.question_text
    if question_data.options is not None:
        question.options = question_data.options
    if question_data.correct_answer is not None:
        question.correct_answer = question_data.correct_answer
    if question_data.difficulty is not None:
        question.difficulty = question_data.difficulty
    if question_data.explanation is not None:
        question.explanation = question_data.explanation
    
    await db.commit()
    await db.refresh(question)
    return QuestionRead.model_validate(question)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a question."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    
    db.delete(question)
    await db.commit()

