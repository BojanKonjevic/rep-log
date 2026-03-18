from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Workout


async def get_all_workouts(
    session: AsyncSession,
    user_id: UUID,
    page: int = 1,
    limit: int = 10,
) -> Sequence[Workout]:
    query = select(Workout).where(Workout.user_id == user_id)
    result = await session.execute(query.offset((page - 1) * limit).limit(limit))
    return result.scalars().all()


async def get_workout(
    session: AsyncSession, workout_id: UUID, user_id: UUID
) -> Workout | None:
    result = await session.execute(
        select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id)
    )
    return result.scalar_one_or_none()
