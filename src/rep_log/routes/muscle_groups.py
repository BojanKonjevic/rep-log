from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import muscle_groups as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import MuscleGroup, User

router = APIRouter(prefix="/muscle_groups", tags=["muscle_groups"])


@router.get("", response_model=Sequence[schemas.MuscleGroupRead])
async def get_all_muscle_groups(
    session: AsyncSession = Depends(get_session),
) -> Sequence[MuscleGroup]:
    return await crud.get_all_muscle_groups(session)


@router.get("/volume", response_model=Sequence[schemas.MuscleGroupVolumeRead])
async def get_muscle_group_volume(
    date_from: date = Query(default=None),
    date_to: date = Query(default=None),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Sequence[schemas.MuscleGroupVolumeRead]:
    return await crud.get_muscle_group_volume(session, date_from, date_to, user.id)
