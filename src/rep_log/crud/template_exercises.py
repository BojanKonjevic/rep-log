from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Exercise, Template, TemplateExercise
from rep_log.schemas import TemplateExerciseCreate


async def create_template_exercise(
    session: AsyncSession,
    template_id: UUID,
    template_exercise: TemplateExerciseCreate,
    user_id: UUID,
) -> TemplateExercise:
    template = (
        await session.execute(
            select(Template).where(
                Template.id == template_id, Template.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not template:
        raise LookupError("Template not found")
    exercise = (
        await session.execute(
            select(Exercise).where(
                Exercise.id == template_exercise.exercise_id,
                Exercise.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if not exercise:
        raise LookupError("Exercise not found")
    db_template_exercise = TemplateExercise(
        template_id=template_id,
        exercise_id=template_exercise.exercise_id,
        order=template_exercise.order,
    )
    session.add(db_template_exercise)
    try:
        await session.commit()
    except IntegrityError as err:
        await session.rollback()
        raise ValueError("An exercise already exists at that position") from err
    await session.refresh(db_template_exercise)
    return db_template_exercise
