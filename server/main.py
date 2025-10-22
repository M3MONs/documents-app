from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import engine, Base

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@app.get("/status")
def get_status() -> dict[str, str]:
    return {"status": "ok"}