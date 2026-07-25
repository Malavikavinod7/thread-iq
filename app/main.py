from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.products import router as v1_router
from app.core.config import settings
from app.core.exceptions import NotFoundError

app = FastAPI(title=settings.project_name)

app.include_router(v1_router, prefix="/api/v1")


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    """Return the service identity."""
    return {"service": settings.project_name}


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a simple health status payload."""
    return {"status": "healthy"}
