from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log import schemas
from rep_log.crud import auth
from rep_log.database import get_session
from rep_log.dependencies import get_current_user
from rep_log.models import User
from rep_log.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead, status_code=201)
async def register(
    body: schemas.UserRegister, session: AsyncSession = Depends(get_session)
) -> schemas.UserRead:
    existing = await auth.get_user_by_email(session, body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email not available")
    user = await auth.create_user(session, body.email, body.password)
    return schemas.UserRead.model_validate(user)


@router.post("/token", response_model=schemas.Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> schemas.Token:
    user = await auth.get_user_by_email(session, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    access_token = create_access_token(user.id)
    refresh_token = await auth.create_refresh_token(session, user.id)
    return schemas.Token(
        access_token=access_token,
        refresh_token=refresh_token.token,
    )


@router.post("/refresh", response_model=schemas.Token)
async def refresh(
    body: schemas.RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> schemas.Token:
    db_token = await auth.get_refresh_token(session, body.refresh_token)
    if not db_token or db_token.revoked:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if db_token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Refresh token expired")
    access_token = create_access_token(db_token.user_id)
    return schemas.Token(
        access_token=access_token,
        refresh_token=body.refresh_token,
    )


@router.post("/logout", status_code=204)
async def logout(
    body: schemas.RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> None:
    await auth.revoke_refresh_token(session, body.refresh_token)


@router.get("/me", response_model=schemas.UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> schemas.UserRead:
    return schemas.UserRead.model_validate(current_user)
