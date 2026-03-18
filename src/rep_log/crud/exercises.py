from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Exercise, MuscleGroup
from rep_log.schemas import ExerciseCreate


async def get_all_exercises(session: AsyncSession, user_id: UUID) -> Sequence[Exercise]:
    result = await session.execute(select(Exercise).where(Exercise.user_id == user_id))
    return result.scalars().all()


async def get_exercises_for_muscle_group(
    session: AsyncSession, muscle_group_name: str, user_id: UUID
) -> Sequence[Exercise]:
    muscle_group = (
        await session.execute(
            select(MuscleGroup).where(MuscleGroup.name == muscle_group_name)
        )
    ).scalar_one_or_none()
    if muscle_group is None:
        raise ValueError("Muscle group not found")
    result = await session.execute(
        select(Exercise).where(
            Exercise.user_id == user_id,
            Exercise.muscle_groups.any(MuscleGroup.name == muscle_group_name),
        )
    )
    return result.scalars().all()


async def get_exercise(
    session: AsyncSession, exercise_id: UUID, user_id: UUID
) -> Exercise | None:
    result = await session.execute(
        select(Exercise).where(Exercise.user_id == user_id, Exercise.id == exercise_id)
    )
    return result.scalar_one_or_none()


async def create_exercise(
    session: AsyncSession, exercise: ExerciseCreate, user_id: UUID
) -> Exercise:
    muscle_group_names = set(exercise.muscle_group_names)
    result = await session.execute(
        select(MuscleGroup).where(MuscleGroup.name.in_(muscle_group_names))
    )
    muscle_groups = result.scalars().all()
    found_names = {mg.name for mg in muscle_groups}
    missing = muscle_group_names - found_names
    if missing:
        raise ValueError(f"Unknown muscle groups: {', '.join(sorted(missing))}")
    db_exercise = Exercise(
        name=exercise.name, muscle_groups=muscle_groups, user_id=user_id
    )
    session.add(db_exercise)
    try:
        await session.commit()
    except IntegrityError as err:
        await session.rollback()
        raise ValueError("Exercise already exists") from err
    await session.refresh(db_exercise, ["muscle_groups"])
    return db_exercise


async def delete_exercise(
    session: AsyncSession, exercise_id: UUID, user_id: UUID
) -> bool:
    db_exercise = (
        await session.execute(
            select(Exercise).where(
                Exercise.id == exercise_id, Exercise.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not db_exercise:
        return False
    await session.delete(db_exercise)
    await session.commit()
    return True
