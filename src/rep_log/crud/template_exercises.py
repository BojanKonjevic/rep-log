from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Exercise, Template, TemplateExercise
from rep_log.schemas import TemplateExerciseCreate, TemplateExerciseUpdate


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


async def update_template_exercise(
    session: AsyncSession,
    template_id: UUID,
    template_exercise_id: UUID,
    template_exercise_update: TemplateExerciseUpdate,
    user_id: UUID,
) -> TemplateExercise | None:
    db_template_exercise = (
        await session.execute(
            select(TemplateExercise)
            .join(Template)
            .where(
                TemplateExercise.id == template_exercise_id,
                TemplateExercise.template_id == template_id,
                Template.user_id == user_id,
            ),
        )
    ).scalar_one_or_none()
    if not db_template_exercise:
        return None
    update_data = template_exercise_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template_exercise, field, value)
    try:
        await session.commit()
    except IntegrityError as err:
        await session.rollback()
        raise ValueError("An exercise already exists at that position") from err
    await session.refresh(db_template_exercise)
    return db_template_exercise
