from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.project_name)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"service": "ThreadIQ"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
