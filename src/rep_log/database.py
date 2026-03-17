from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI
from sqlalchemy import Uuid, func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .settings import settings

MUSCLE_GROUPS = [
    "chest",
    "back",
    "delts",
    "traps",
    "biceps",
    "triceps",
    "forearms",
    "abs",
    "lower back",
    "glutes",
    "quadriceps",
    "hamstrings",
    "calves",
    "adductors",
    "abductors",
    "hip flexors",
    "neck",
]
engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)


class BaseModel(UUIDPrimaryKeyMixin, Base):
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
