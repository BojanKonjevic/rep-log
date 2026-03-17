from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rep_log.models import RefreshToken, User
from rep_log.security import generate_refresh_token, hash_password
from rep_log.settings import settings


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    user = User(email=email, hashed_password=hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_refresh_token(session: AsyncSession, user_id: UUID) -> RefreshToken:
    token = RefreshToken(
        token=generate_refresh_token(),
        user_id=user_id,
        expires_at=datetime.now(UTC).replace(tzinfo=None)
        + timedelta(days=settings.refresh_token_expire_days),
    )
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return token


async def get_refresh_token(session: AsyncSession, token: str) -> RefreshToken | None:
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token == token)
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(session: AsyncSession, token: str) -> bool:
    db_token = await get_refresh_token(session, token)
    if db_token is None:
        return False
    db_token.revoked = True
    await session.commit()
    return True
