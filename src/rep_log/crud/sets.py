from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Set, Workout, WorkoutExercise
from rep_log.schemas import SetCreate


async def create_set(
    session: AsyncSession,
    set_create: SetCreate,
    user_id: UUID,
) -> Set:
    workout_exercise = (
        await session.execute(
            select(WorkoutExercise)
            .join(Workout)
            .where(
                WorkoutExercise.id == set_create.workout_exercise_id,
                Workout.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if not workout_exercise:
        raise LookupError("Workout exercise not found")
    db_set = Set(
        set_number=set_create.set_number,
        reps=set_create.reps,
        weight=set_create.weight,
        workout_exercise_id=set_create.workout_exercise_id,
    )
    session.add(db_set)
    try:
        await session.commit()
    except IntegrityError as err:
        await session.rollback()
        raise ValueError("Set already exists at that position") from err
    await session.refresh(db_set)
    return db_set
