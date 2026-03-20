from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import sets as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import Set, User

router = APIRouter(prefix="/sets", tags=["sets"])


@router.post(
    "",
    response_model=schemas.SetRead,
    status_code=201,
)
async def create_set(
    set_create: schemas.SetCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Set:
    try:
        return await crud.create_set(session, set_create, user.id)
    except LookupError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err


@router.patch(
    "/{set_id}",
    response_model=schemas.SetRead,
)
async def update_set(
    set_id: UUID,
    set_update: schemas.SetUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Set:
    try:
        updated_set = await crud.update_set(session, set_id, set_update, user.id)
        if not updated_set:
            raise HTTPException(status_code=404, detail="Set not found")
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    return updated_set
