from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Exercise, MuscleGroup, Workout, WorkoutExercise
from rep_log.schemas import WorkoutCreate, WorkoutUpdate


async def get_all_workouts(
    session: AsyncSession,
    user_id: UUID,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    exercise_ids: Sequence[UUID] | None = None,
    muscle_group_names: Sequence[str] | None = None,
    page: int = 1,
    limit: int = 10,
) -> Sequence[Workout]:
    query = select(Workout).where(Workout.user_id == user_id)
    if search:
        query = query.where(
            or_(Workout.name.ilike(f"%{search}%"), Workout.notes.ilike(f"%{search}%"))
        )
    if date_from is not None:
        query = query.where(Workout.workout_date >= date_from)
    if date_to is not None:
        query = query.where(Workout.workout_date <= date_to)
    if exercise_ids:
        query = query.where(
            Workout.exercises.any(WorkoutExercise.exercise_id.in_(exercise_ids))
        )
    if muscle_group_names:
        query = query.where(
            Workout.exercises.any(
                WorkoutExercise.exercise.has(
                    Exercise.muscle_groups.any(MuscleGroup.name.in_(muscle_group_names))
                )
            )
        )
    result = await session.execute(
        query.offset((page - 1) * limit)
        .limit(limit)
        .order_by(Workout.workout_date.desc(), Workout.id)
    )
    return result.scalars().all()


async def get_workout(
    session: AsyncSession, workout_id: UUID, user_id: UUID
) -> Workout | None:
    result = await session.execute(
        select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_workout(
    session: AsyncSession, workout: WorkoutCreate, user_id: UUID
) -> Workout:
    db_workout = Workout(
        name=workout.name,
        workout_date=workout.workout_date,
        notes=workout.notes,
        user_id=user_id,
    )
    session.add(db_workout)
    await session.commit()
    await session.refresh(db_workout)
    return db_workout


async def update_workout(
    session: AsyncSession,
    workout_id: UUID,
    workout_update: WorkoutUpdate,
    user_id: UUID,
) -> Workout | None:
    db_workout = (
        await session.execute(
            select(Workout).where(
                Workout.id == workout_id,
                Workout.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if not db_workout:
        return None
    update_data = workout_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_workout, field, value)
    await session.commit()
    await session.refresh(db_workout)
    return db_workout


async def delete_workout(
    session: AsyncSession, workout_id: UUID, user_id: UUID
) -> bool:
    db_workout = (
        await session.execute(
            select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id)
        )
    ).scalar_one_or_none()
    if not db_workout:
        return False
    await session.delete(db_workout)
    await session.commit()
    return True
