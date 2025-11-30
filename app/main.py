from fastapi import FastAPI
from app.api.v1.routes import router as api_router


app = FastAPI(title="AI Resume Analyst API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")