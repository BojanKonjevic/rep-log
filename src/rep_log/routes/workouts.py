from collections.abc import Sequence
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import workouts as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import User, Workout

router = APIRouter(
    prefix="/workouts",
    tags=["workouts"],
    responses={200: {"headers": {"X-Total-Count": {"schema": {"type": "integer"}}}}},
)


@router.get("", response_model=Sequence[schemas.WorkoutRead])
async def get_all_workouts(
    response: Response,
    search: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    exercise_ids: Sequence[UUID] | None = Query(default=None),
    muscle_group_names: Sequence[str] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Sequence[Workout]:
    workouts, total = await crud.get_all_workouts(
        session,
        user.id,
        search,
        date_from,
        date_to,
        exercise_ids,
        muscle_group_names,
        page,
        limit,
    )
    response.headers["X-Total-Count"] = str(total)
    return workouts


@router.get("/streak", response_model=int)
async def get_streak(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> int:
    return await crud.get_streak(session, user.id)


@router.get("/setcounts", response_model=Sequence[schemas.SetCountPerWorkoutRead])
async def get_set_count_per_workout(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> Sequence[schemas.SetCountPerWorkoutRead]:
    return await crud.get_set_count_per_workout(session, user.id, date_from, date_to)


@router.get("/{workout_id}", response_model=schemas.WorkoutRead)
async def get_workout(
    workout_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Workout | None:
    workout = await crud.get_workout(session, workout_id, user.id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.post("", response_model=schemas.WorkoutRead, status_code=201)
async def create_workout(
    workout: schemas.WorkoutCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Workout:
    return await crud.create_workout(session, workout, user.id)


@router.patch("/{workout_id}", response_model=schemas.WorkoutRead)
async def update_workout(
    workout_id: UUID,
    workout_update: schemas.WorkoutUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Workout:
    updated_workout = await crud.update_workout(
        session, workout_id, workout_update, user.id
    )
    if not updated_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return updated_workout


@router.delete("/{workout_id}", status_code=204)
async def delete_workout(
    workout_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    deleted = await crud.delete_workout(session, workout_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workout not found")
