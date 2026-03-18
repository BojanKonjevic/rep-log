from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import workouts as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import User, Workout

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("", response_model=Sequence[schemas.WorkoutRead])
async def get_all_workouts(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Sequence[Workout]:
    return await crud.get_all_workouts(session, user.id)


@router.get("/{workout_id}", response_model=schemas.WorkoutRead)
async def get_workout(
    workout_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Workout | None:
    workout = await crud.get_workout(session, workout_id, user.id)
    if workout is None:
        raise HTTPException(status_code=404, detail="workout not found")
    return workout
