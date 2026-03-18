from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import exercises as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import Exercise, User

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=Sequence[schemas.ExerciseRead])
async def get_all_exercises(
    user: User = Depends(get_current_user),
    muscle_group_name: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> Sequence[Exercise]:
    if muscle_group_name is not None:
        try:
            return await crud.get_exercises_for_muscle_group(
                session, muscle_group_name, user.id
            )
        except ValueError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err
    return await crud.get_all_exercises(session, user.id)


@router.get("/{exercise_id}", response_model=schemas.ExerciseRead)
async def get_exercise(
    exercise_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Exercise | None:
    exercise = await crud.get_exercise(session, exercise_id, user.id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.post("", response_model=schemas.ExerciseRead, status_code=201)
async def create_exercise(
    exercise: schemas.ExerciseCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Exercise:
    try:
        return await crud.create_exercise(session, exercise, user.id)
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err


@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    deleted = await crud.delete_exercise(session, exercise_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exercise not found")
