from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
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


@router.get("", response_model=Sequence[schemas.TemplateRead])
async def get_all_templates(
    search: str | None = Query(default=None),
    exercise_ids: Sequence[UUID] | None = Query(default=None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Sequence[Template]:
    templates = await crud.get_all_templates(
        session,
        user.id,
        search,
        exercise_ids,
    )
    return templates


@router.get("/{template_id}", response_model=schemas.TemplateRead)
async def get_template(
    template_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Template | None:
    template = await crud.get_template(session, template_id, user.id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.patch("/{template_id}", response_model=schemas.TemplateRead)
async def update_template(
    template_id: UUID,
    template_update: schemas.TemplateUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Template:
    updated_template = await crud.update_template(
        session, template_id, template_update, user.id
    )
    if not updated_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated_template
