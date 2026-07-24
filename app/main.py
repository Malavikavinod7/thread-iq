from fastapi import FastAPI

app = FastAPI(title="ThreadIQ")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"service": "ThreadIQ"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
