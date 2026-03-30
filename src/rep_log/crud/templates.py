from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Template, TemplateExercise, Workout, WorkoutExercise
from rep_log.schemas import TemplateCreate, TemplateUpdate, WorkoutCreate


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


async def get_template(
    session: AsyncSession, template_id: UUID, user_id: UUID
) -> Template | None:
    result = await session.execute(
        select(Template).where(Template.id == template_id, Template.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_template(
    session: AsyncSession,
    template_id: UUID,
    template_update: TemplateUpdate,
    user_id: UUID,
) -> Template | None:
    db_template = (
        await session.execute(
            select(Template).where(
                Template.id == template_id,
                Template.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if not db_template:
        return None
    update_data = template_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    await session.commit()
    await session.refresh(db_template)
    return db_template


async def delete_template(
    session: AsyncSession, template_id: UUID, user_id: UUID
) -> bool:
    db_template = (
        await session.execute(
            select(Template).where(
                Template.id == template_id, Template.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not db_template:
        return False
    await session.delete(db_template)
    await session.commit()
    return True


async def create_workout_from_template(
    session: AsyncSession, user_id: UUID, template_id: UUID, workout: WorkoutCreate
) -> Workout:
    template = (
        await session.execute(
            select(Template).where(
                Template.id == template_id, Template.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not template:
        raise LookupError("Template not found")
    db_workout = Workout(
        name=workout.name,
        workout_date=workout.workout_date,
        notes=workout.notes,
        user_id=user_id,
    )
    exercises = template.exercises
    for exercise in exercises:
        db_workout.exercises.append(
            WorkoutExercise(
                workout=db_workout,
                exercise_id=exercise.exercise_id,
                order=exercise.order,
            )
        )
    session.add(db_workout)
    await session.commit()
    await session.refresh(db_workout)
    return db_workout
