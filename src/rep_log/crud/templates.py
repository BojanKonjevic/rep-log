from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Template, TemplateExercise
from rep_log.schemas import TemplateCreate


async def create_template(
    session: AsyncSession, template: TemplateCreate, user_id: UUID
) -> Template:
    db_template = Template(
        name=template.name,
        user_id=user_id,
    )
    session.add(db_template)
    await session.commit()
    await session.refresh(db_template)
    return db_template


async def get_all_templates(
    session: AsyncSession,
    user_id: UUID,
    search: str | None = None,
    exercise_ids: Sequence[UUID] | None = None,
) -> Sequence[Template]:
    query = select(Template).where(Template.user_id == user_id)
    if search:
        search_filter = Template.name.ilike(f"%{search}%")
        query = query.where(search_filter)
    if exercise_ids:
        exercises_filter = Template.exercises.any(
            TemplateExercise.exercise_id.in_(exercise_ids)
        )
        query = query.where(exercises_filter)
    result = await session.execute(query)
    return result.scalars().all()
