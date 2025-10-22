from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
from core.database import engine, Base
from models import organization, department, role, user  # noqa: F401
from routes import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/status")
def get_status() -> dict[str, str]:
    return {"status": "ok"}

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)

app.include_router(api_router)