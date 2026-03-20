from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Exercise, Workout, WorkoutExercise
from rep_log.schemas import WorkoutExerciseCreate


async def create_workout_exercise(
    session: AsyncSession,
    workout_id: UUID,
    workout_exercise: WorkoutExerciseCreate,
    user_id: UUID,
) -> WorkoutExercise:
    workout = (
        await session.execute(
            select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id)
        )
    ).scalar_one_or_none()
    if not workout:
        raise LookupError("Workout not found")
    exercise = (
        await session.execute(
            select(Exercise).where(
                Exercise.id == workout_exercise.exercise_id, Exercise.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not exercise:
        raise LookupError("Exercise not found")
    db_workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=workout_exercise.exercise_id,
        order=workout_exercise.order,
    )
    session.add(db_workout_exercise)
    try:
        await session.commit()
    except IntegrityError as err:
        await session.rollback()
        raise ValueError("An exercise already exists at that position") from err
    await session.refresh(db_workout_exercise)
    return db_workout_exercise
