from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import func, or_, select
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
) -> tuple[Sequence[Workout], int]:
    query = select(Workout).where(Workout.user_id == user_id)
    countQuery = (
        select(func.count()).select_from(Workout).where(Workout.user_id == user_id)
    )
    if search:
        searchFilter = or_(
            Workout.name.ilike(f"%{search}%"), Workout.notes.ilike(f"%{search}%")
        )
        query = query.where(searchFilter)
        countQuery = countQuery.where(searchFilter)
    if date_from is not None:
        date_from_filter = Workout.workout_date >= date_from
        query = query.where(date_from_filter)
        countQuery = countQuery.where(date_from_filter)
    if date_to is not None:
        date_to_filter = Workout.workout_date <= date_to
        query = query.where(date_to_filter)
        countQuery = countQuery.where(date_to_filter)
    if exercise_ids:
        exercisesFilter = Workout.exercises.any(
            WorkoutExercise.exercise_id.in_(exercise_ids)
        )
        query = query.where(exercisesFilter)
        countQuery = countQuery.where(exercisesFilter)
    if muscle_group_names:
        muscle_groups_filter = Workout.exercises.any(
            WorkoutExercise.exercise.has(
                Exercise.muscle_groups.any(MuscleGroup.name.in_(muscle_group_names))
            )
        )
        query = query.where(muscle_groups_filter)
        countQuery = countQuery.where(muscle_groups_filter)
    result = await session.execute(
        query.offset((page - 1) * limit)
        .limit(limit)
        .order_by(Workout.workout_date.desc(), Workout.id)
    )
    countResult = await session.execute(countQuery)
    count = countResult.scalar_one()
    return (result.scalars().all(), count)


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
