from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import templates as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import Template, User

router = APIRouter(
    prefix="/templates",
    tags=["templates"],
)


@router.post("", response_model=schemas.TemplateRead, status_code=201)
async def create_template(
    template: schemas.TemplateCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Template:
    return await crud.create_template(session, template, user.id)
