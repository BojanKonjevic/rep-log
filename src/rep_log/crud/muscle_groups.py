from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import (
    Exercise,
    MuscleGroup,
    Set,
    Workout,
    WorkoutExercise,
    exercise_muscle_group,
)
from rep_log.schemas import MuscleGroupVolumeRead, MuscleGroupWeekRead


async def get_all_muscle_groups(session: AsyncSession) -> Sequence[MuscleGroup]:
    result = await session.execute(select(MuscleGroup))
    return result.scalars().all()


async def get_muscle_group_volume(
    session: AsyncSession,
    date_from: date | None,
    date_to: date | None,
    user_id: UUID,
) -> Sequence[MuscleGroupVolumeRead]:
    volume_query = (
        select(
            MuscleGroup.id,
            func.date_trunc(literal_column("'week'"), Workout.workout_date).label(
                "week_start"
            ),
            func.count().label("set_count"),
        )
        .select_from(Set)
        .join(WorkoutExercise)
        .join(Workout)
        .join(Exercise)
        .join(exercise_muscle_group)
        .join(MuscleGroup)
        .where(Workout.user_id == user_id)
        .group_by(
            MuscleGroup.id,
            func.date_trunc(literal_column("'week'"), Workout.workout_date),
        )
        .order_by(
            MuscleGroup.id,
            func.date_trunc(literal_column("'week'"), Workout.workout_date),
        )
    )
    if date_from is not None:
        volume_query = volume_query.where(Workout.workout_date >= date_from)
    if date_to is not None:
        volume_query = volume_query.where(Workout.workout_date <= date_to)
    result = (await session.execute(volume_query)).all()
    grouped: dict[UUID, MuscleGroupVolumeRead] = {}
    for row in result:
        if row.id in grouped:
            grouped[row.id].all_weeks.append(
                MuscleGroupWeekRead(
                    week_start=row.week_start, weekly_sets=row.set_count
                )
            )
        else:
            grouped[row.id] = MuscleGroupVolumeRead(
                muscle_group_id=row.id,
                all_weeks=[
                    MuscleGroupWeekRead(
                        week_start=row.week_start, weekly_sets=row.set_count
                    )
                ],
            )
    return list(grouped.values())
