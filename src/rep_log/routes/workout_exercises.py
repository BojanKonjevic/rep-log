from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import workout_exercises as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import User, WorkoutExercise

router = APIRouter(prefix="/workouts", tags=["workout_exercises"])


@router.post(
    "/{workout_id}/exercises",
    response_model=schemas.WorkoutExerciseRead,
    status_code=201,
)
async def create_workout_exercise(
    workout_id: UUID,
    workout_exercise: schemas.WorkoutExerciseCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorkoutExercise:
    try:
        return await crud.create_workout_exercise(
            session, workout_id, workout_exercise, user.id
        )
    except LookupError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err


@router.patch(
    "/{workout_id}/exercises/{workout_exercise_id}",
    response_model=schemas.WorkoutExerciseRead,
)
async def update_workout_exercise(
    workout_id: UUID,
    workout_exercise_id: UUID,
    workout_exercise_update: schemas.WorkoutExerciseUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorkoutExercise:
    try:
        updated_workout_exercise = await crud.update_workout_exercise(
            session, workout_id, workout_exercise_id, workout_exercise_update, user.id
        )
        if not updated_workout_exercise:
            raise HTTPException(status_code=404, detail="Workout exercise not found")
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    return updated_workout_exercise


@router.delete("/{workout_id}/exercises/{workout_exercise_id}", status_code=204)
async def delete_workout_exercise(
    workout_id: UUID,
    workout_exercise_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    deleted = await crud.delete_workout_exercise(
        session, workout_id, workout_exercise_id, user.id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Workout exercise not found")
