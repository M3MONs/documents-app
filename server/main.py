from contextlib import asynccontextmanager
import logging
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from core.database import engine, Base
from models import organization, department, role, user  # noqa: F401
from routes import auth
from routes.admin import admin_user, admin_organization, admin_department, admin_role


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.error(f"Unhandled exception for {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"})


@app.get("/status")
def get_status() -> dict[str, str]:
    return {"status": "ok"}


api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)

api_router.include_router(admin_user.router)
api_router.include_router(admin_organization.router)
api_router.include_router(admin_department.router)
api_router.include_router(admin_role.router)

app.include_router(api_router)
