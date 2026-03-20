from fastapi import FastAPI

from rep_log.database import lifespan
from rep_log.routes.auth import router as auth_router
from rep_log.routes.exercises import router as exercises_router
from rep_log.routes.muscle_groups import router as muscle_groups_router
from rep_log.routes.workouts import router as workouts_router

app = FastAPI(lifespan=lifespan)
app.include_router(workouts_router)
app.include_router(exercises_router)
app.include_router(muscle_groups_router)
app.include_router(auth_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
