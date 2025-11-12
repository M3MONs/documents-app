from contextlib import asynccontextmanager
import logging
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from core.database import engine, Base, AsyncSessionLocal
from models import organization, department, role, user, category, folder, document  # noqa: F401
from routes import auth
from routes.admin import admin_user, admin_organization, admin_department, admin_role, admin_user_organization_role
from core.roles import StaticRole
from schemas.role import RoleCreatePayload
from services.role_service import RoleService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        for role_data in StaticRole.all_roles():
            if await RoleService.is_unique_name(db, role_data["name"]):
                payload = RoleCreatePayload(**role_data)
                await RoleService.create_role(db, payload)
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
api_router.include_router(admin_user_organization_role.router)

app.include_router(api_router)
