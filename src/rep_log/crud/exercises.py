from collections.abc import Sequence
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import Exercise, MuscleGroup, Set, Workout, WorkoutExercise
from rep_log.schemas import ExerciseCreate, ExercisePRsRead, ExerciseUpdate


class MuscleGroupNotFound(Exception):
    pass


async def get_all_exercises(
    session: AsyncSession, user_id: UUID, page: int = 1, limit: int = 10
) -> Sequence[Exercise]:
    query = select(Exercise).where(Exercise.user_id == user_id)
    result = await session.execute(query.offset((page - 1) * limit).limit(limit))
    return result.scalars().all()


async def get_exercises_for_muscle_group(
    session: AsyncSession,
    muscle_group_name: str,
    user_id: UUID,
    page: int = 1,
    limit: int = 10,
) -> Sequence[Exercise]:
    result = await session.execute(
        select(Exercise)
        .where(
            Exercise.user_id == user_id,
            Exercise.muscle_groups.any(MuscleGroup.name == muscle_group_name),
        )
        .offset((page - 1) * limit)
        .limit(limit)
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
        raise MuscleGroupNotFound(
            f"Unknown muscle groups: {', '.join(sorted(missing))}"
        )
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


async def update_exercise(
    session: AsyncSession,
    exercise_id: UUID,
    exercise_update: ExerciseUpdate,
    user_id: UUID,
) -> Exercise | None:
    db_exercise = (
        await session.execute(
            select(Exercise).where(
                Exercise.id == exercise_id, Exercise.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not db_exercise:
        return None
    update_data = exercise_update.model_dump(exclude_unset=True)
    updated_muscle_groups = update_data.pop("muscle_group_names", None)
    if updated_muscle_groups is not None:
        muscle_group_names = set(updated_muscle_groups)
        result = await session.execute(
            select(MuscleGroup).where(MuscleGroup.name.in_(muscle_group_names))
        )
        muscle_groups = result.scalars().all()
        found_names = {mg.name for mg in muscle_groups}
        missing = muscle_group_names - found_names
        if missing:
            raise MuscleGroupNotFound(
                f"Unknown muscle groups: {', '.join(sorted(missing))}"
            )
        db_exercise.muscle_groups = list(muscle_groups)
    for field, value in update_data.items():
        setattr(db_exercise, field, value)
    try:
        await session.commit()
    except IntegrityError as err:
        await session.rollback()
        raise ValueError("Exercise already exists") from err
    await session.refresh(db_exercise, ["muscle_groups"])
    return db_exercise


async def get_exercise_prs(
    session: AsyncSession, exercise_id: UUID, user_id: UUID
) -> Sequence[ExercisePRsRead]:
    subq = (
        select(
            Set.reps,
            Set.weight,
            Workout.workout_date,
            Workout.id,
            func.row_number()
            .over(
                partition_by=Set.reps,
                order_by=(Set.weight.desc(), Workout.workout_date.desc()),
            )
            .label("row_number"),
        )
        .select_from(Set)
        .join(WorkoutExercise)
        .join(Workout)
        .where(WorkoutExercise.exercise_id == exercise_id)
        .where(Workout.user_id == user_id)
        .subquery()
    )
    result = await session.execute(select(subq).where(subq.c.row_number == 1))
    response = []
    for row in result.all():
        response.append(
            ExercisePRsRead(
                reps=row.reps,
                weight=row.weight,
                estimated_1rm=(
                    row.weight * (1 + Decimal(row.reps) / Decimal(30))
                ).quantize(Decimal("0.01")),
                achieved_on=row.workout_date,
                workout_id=row.id,
            )
        )
    return response
