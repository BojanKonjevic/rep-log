from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Template
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
