from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import MuscleGroup


async def get_all_muscle_groups(session: AsyncSession) -> Sequence[MuscleGroup]:
    result = await session.execute(select(MuscleGroup))
    return result.scalars().all()
