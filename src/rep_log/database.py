from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI
from sqlalchemy import DateTime, Dialect, Uuid, func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from rep_log.seed import MUSCLE_GROUPS
from rep_log.settings import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class TZDateTime(TypeDecorator[datetime]):
    impl = DateTime
    cache_ok = True

    def process_bind_param(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        """Strip tzinfo before writing - store as naive UTC"""
        if value is not None and value.tzinfo is not None:
            return value.astimezone(UTC).replace(tzinfo=None)
        return value

    def process_result_value(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        """Re-attach UTC when reading back"""
        if value is not None:
            return value.replace(tzinfo=UTC)
        return value


class Base(DeclarativeBase):
    pass


class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)


class DBModel(UUIDPrimaryKeyMixin, Base):
    __abstract__ = True


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from rep_log.models import MuscleGroup

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(MuscleGroup))
        if result.scalar() == 0:
            session.add_all([MuscleGroup(name=name) for name in MUSCLE_GROUPS])
            await session.commit()
    yield
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
