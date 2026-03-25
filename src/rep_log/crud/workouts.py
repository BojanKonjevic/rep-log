from collections.abc import Sequence
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func, literal_column, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Exercise, MuscleGroup, Set, Workout, WorkoutExercise
from rep_log.schemas import SetCountPerWorkoutRead, WorkoutCreate, WorkoutUpdate


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
    count_query = (
        select(func.count()).select_from(Workout).where(Workout.user_id == user_id)
    )
    if search:
        search_filter = or_(
            Workout.name.ilike(f"%{search}%"), Workout.notes.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    if date_from is not None:
        date_from_filter = Workout.workout_date >= date_from
        query = query.where(date_from_filter)
        count_query = count_query.where(date_from_filter)
    if date_to is not None:
        date_to_filter = Workout.workout_date <= date_to
        query = query.where(date_to_filter)
        count_query = count_query.where(date_to_filter)
    if exercise_ids:
        exercises_filter = Workout.exercises.any(
            WorkoutExercise.exercise_id.in_(exercise_ids)
        )
        query = query.where(exercises_filter)
        count_query = count_query.where(exercises_filter)
    if muscle_group_names:
        muscle_groups_filter = Workout.exercises.any(
            WorkoutExercise.exercise.has(
                Exercise.muscle_groups.any(MuscleGroup.name.in_(muscle_group_names))
            )
        )
        query = query.where(muscle_groups_filter)
        count_query = count_query.where(muscle_groups_filter)
    result = await session.execute(
        query.offset((page - 1) * limit)
        .limit(limit)
        .order_by(Workout.workout_date.desc(), Workout.id)
    )
    count_result = await session.execute(count_query)
    count = count_result.scalar_one()
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


async def get_streak(session: AsyncSession, user_id: UUID) -> int:
    workout_weeks = (
        select(
            func.date_trunc(literal_column("'week'"), Workout.workout_date).label(
                "week_start"
            )
        )
        .where(Workout.user_id == user_id)
        .distinct()
        .subquery()
    )

    most_recent_week = (
        await session.execute(
            select(func.date_trunc(literal_column("'week'"), Workout.workout_date))
            .where(Workout.user_id == user_id)
            .order_by(
                func.date_trunc(literal_column("'week'"), Workout.workout_date).desc()
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if most_recent_week:
        most_recent_week = most_recent_week.date()
    current_week = date.today() - timedelta(days=date.today().weekday())
    last_week = date.today() - timedelta(days=(date.today().weekday() + 7))
    if most_recent_week != current_week and most_recent_week != last_week:
        return 0

    anchor = select(workout_weeks).order_by(workout_weeks.c.week_start.desc()).limit(1)
    streak_cte = anchor.cte(recursive=True)
    recursive_part = select(workout_weeks).where(
        workout_weeks.c.week_start
        == (streak_cte.c.week_start - text("interval '7 days'"))
    )
    streak_cte = streak_cte.union_all(recursive_part)
    result = await session.execute(select(func.count()).select_from(streak_cte))
    return result.scalar_one()


async def get_set_count_per_workout(
    session: AsyncSession,
    user_id: UUID,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Sequence[SetCountPerWorkoutRead]:
    query = (
        select(func.count(Set.id).label("set_count"), Workout.id, Workout.workout_date)
        .select_from(Set)
        .join(WorkoutExercise)
        .join(Workout)
        .where(Workout.user_id == user_id)
        .group_by(Workout.id)
        .order_by(Workout.workout_date)
    )
    if date_from is not None:
        date_from_filter = Workout.workout_date >= date_from
        query = query.where(date_from_filter)
    if date_to is not None:
        date_to_filter = Workout.workout_date <= date_to
        query = query.where(date_to_filter)
    rows = await session.execute(query)
    all_counts: list[SetCountPerWorkoutRead] = []
    for row in rows.all():
        all_counts.append(
            SetCountPerWorkoutRead(
                workout_id=row.id,
                workout_date=row.workout_date,
                set_count=row.set_count,
            )
        )
    return all_counts
