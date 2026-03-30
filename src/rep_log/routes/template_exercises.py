from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import template_exercises as crud
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import TemplateExercise, User

router = APIRouter(prefix="/templates", tags=["template_exercises"])


@router.post(
    "/{template_id}/exercises",
    response_model=schemas.TemplateExerciseRead,
    status_code=201,
)
async def create_template_exercise(
    template_id: UUID,
    template_exercise: schemas.TemplateExerciseCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TemplateExercise:
    try:
        return await crud.create_template_exercise(
            session, template_id, template_exercise, user.id
        )
    except LookupError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err


@router.patch(
    "/{template_id}/exercises/{template_exercise_id}",
    response_model=schemas.TemplateExerciseRead,
)
async def update_template_exercise(
    template_id: UUID,
    template_exercise_id: UUID,
    template_exercise_update: schemas.TemplateExerciseUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TemplateExercise:
    try:
        update_template_exercise = await crud.update_template_exercise(
            session,
            template_id,
            template_exercise_id,
            template_exercise_update,
            user.id,
        )
        if not update_template_exercise:
            raise HTTPException(status_code=404, detail="Template exercise not found")
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    return update_template_exercise
