from fastapi import Depends, FastAPI

from rep_log.database import lifespan
from rep_log.dependencies import get_current_user
from rep_log.models import User
from rep_log.routes.auth import router as auth_router
from rep_log.routes.muscle_groups import router as muscle_groups_router
from rep_log.schemas import UserRead

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(muscle_groups_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
