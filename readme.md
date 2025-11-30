docker compose build

docker compose exec api bash


alembic init alembic

docker compose exec db psql -U postgres -d resumedb

CREATE EXTENSION IF NOT EXISTS vector;

alembic revision --autogenerate -m "init schema"
alembic upgrade head

docker compose exec api python -m ingestion.ingest_initial_resumes


