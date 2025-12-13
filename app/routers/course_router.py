from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.course_model import Course
from app.models.user import User
from app.schemas.course_schema import CourseCreate, CourseRead, CourseUpdate
from app.utils.dependencies import get_current_user

router = APIRouter(tags=["courses"])


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseRead:
    """Create a new course."""
    db_course = Course(
        title=course_data.title,
        description=course_data.description,
    )
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return CourseRead.model_validate(db_course)


@router.get("/", response_model=List[CourseRead])
async def get_all_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CourseRead]:
    """Get all courses."""
    result = await db.execute(select(Course))
    courses = result.scalars().all()
    return [CourseRead.model_validate(course) for course in courses]


@router.get("/{course_id}", response_model=CourseRead)
async def get_course_by_id(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseRead:
    """Get a course by ID."""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    return CourseRead.model_validate(course)


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: uuid.UUID,
    course_data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseRead:
    """Update a course."""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    # Update fields if provided
    if course_data.title is not None:
        course.title = course_data.title
    if course_data.description is not None:
        course.description = course_data.description
    
    await db.commit()
    await db.refresh(course)
    return CourseRead.model_validate(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a course."""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    db.delete(course)
    await db.commit()

