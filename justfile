test:
    pytest -v
cov:
    pytest --cov=src --cov-report=term-missing
lint:
    ruff check .
fmt:
    ruff format .
check:
    mypy .
run:
    uvicorn rep_log.main:app --reload

migrate msg="":
    alembic revision --autogenerate -m "{{msg}}"
upgrade:
    alembic upgrade head
downgrade:
    alembic downgrade -1
db-drop:
    dropdb rep-log

fe:
    cd frontend && npm run dev
fe-build:
    cd frontend && npm run build
fe-install:
    cd frontend && npm install
