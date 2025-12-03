from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from typing import Any

from app.models.chapter_model import Chapter
from app.models.course_model import Course
from app.models.user import User
from app.schemas.chapter_schema import ChapterCreate, ChapterRead, ChapterUpdate
from app.utils.database import get_db
from app.utils.dependencies import get_current_user

router = APIRouter(tags=["chapters"])


@router.post("/", response_model=ChapterRead, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    chapter_data: ChapterCreate,
    db: Any = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChapterRead:
    """Create a new chapter inside a course."""
    # Verify course exists
    result = await db.execute(select(Course).where(Course.id == chapter_data.course_id))
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    db_chapter = Chapter(
        course_id=chapter_data.course_id,
        title=chapter_data.title,
        description=chapter_data.description,
        order_index=chapter_data.order_index,
    )
    db.add(db_chapter)
    await db.commit()
    await db.refresh(db_chapter)
    return ChapterRead.model_validate(db_chapter)


@router.get("/course/{course_id}", response_model=List[ChapterRead])
async def get_chapters_by_course_id(
    course_id: uuid.UUID,
    db: Any = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ChapterRead]:
    """Get all chapters for a specific course."""
    # Verify course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    result = await db.execute(
        select(Chapter)
        .where(Chapter.course_id == course_id)
        .order_by(Chapter.order_index)
    )
    chapters = result.scalars().all()
    return [ChapterRead.model_validate(chapter) for chapter in chapters]


@router.get("/{chapter_id}", response_model=ChapterRead)
async def get_chapter_by_id(
    chapter_id: uuid.UUID,
    db: Any = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChapterRead:
    """Get a chapter by ID."""
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )
    
    return ChapterRead.model_validate(chapter)


@router.put("/{chapter_id}", response_model=ChapterRead)
async def update_chapter(
    chapter_id: uuid.UUID,
    chapter_data: ChapterUpdate,
    db: Any = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChapterRead:
    """Update a chapter."""
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )
    
    # Verify course exists if course_id is being updated
    if chapter_data.course_id is not None:
        course_result = await db.execute(
            select(Course).where(Course.id == chapter_data.course_id)
        )
        course = course_result.scalar_one_or_none()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        chapter.course_id = chapter_data.course_id
    
    # Update fields if provided
    if chapter_data.title is not None:
        chapter.title = chapter_data.title
    if chapter_data.description is not None:
        chapter.description = chapter_data.description
    if chapter_data.order_index is not None:
        chapter.order_index = chapter_data.order_index
    
    await db.commit()
    await db.refresh(chapter)
    return ChapterRead.model_validate(chapter)


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    chapter_id: uuid.UUID,
    db: Any = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a chapter."""
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )
    
    db.delete(chapter)
    await db.commit()

