from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import exercises as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import Exercise, User

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=Sequence[schemas.ExerciseRead])
async def get_all_exercises(
    muscle_group_name: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Sequence[Exercise]:
    if muscle_group_name is not None:
        return await crud.get_exercises_for_muscle_group(
            session, muscle_group_name, user.id, page, limit
        )
    return await crud.get_all_exercises(session, user.id, page, limit)


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


@router.get("/{exercise_id}/pr", response_model=Sequence[schemas.ExercisePRsRead])
async def get_exercise_prs(
    exercise_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Sequence[schemas.ExercisePRsRead]:
    exercise = await crud.get_exercise(session, exercise_id, user.id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return await crud.get_exercise_prs(session, exercise_id, user.id)


@router.post("", response_model=schemas.ExerciseRead, status_code=201)
async def create_exercise(
    exercise: schemas.ExerciseCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Exercise:
    try:
        return await crud.create_exercise(session, exercise, user.id)
    except crud.MuscleGroupNotFound as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
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


@router.patch("/{exercise_id}", response_model=schemas.ExerciseRead)
async def update_exercise(
    exercise_id: UUID,
    exercise_update: schemas.ExerciseUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Exercise:
    try:
        updated_exercise = await crud.update_exercise(
            session, exercise_id, exercise_update, user.id
        )
    except crud.MuscleGroupNotFound as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    if not updated_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return updated_exercise
