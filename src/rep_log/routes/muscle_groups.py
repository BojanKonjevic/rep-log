from collections.abc import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import muscle_groups as crud
from rep_log.database import get_session
from rep_log.models import MuscleGroup

router = APIRouter(prefix="/muscle_groups", tags=["muscle_groups"])


@router.get("", response_model=Sequence[schemas.MuscleGroupRead])
async def get_all_muscle_groups(
    session: AsyncSession = Depends(get_session),
) -> Sequence[MuscleGroup]:
    return await crud.get_all_muscle_groups(session)
