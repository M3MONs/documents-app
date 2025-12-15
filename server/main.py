from contextlib import asynccontextmanager
import logging
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base, AsyncSessionLocal
from models import organization, department, role, user, category, folder, document  # noqa: F401
from routes import auth, category as category_router, organization as organization_router, document as document_router
from routes.admin import (
    admin_user,
    admin_organization,
    admin_department,
    admin_role,
    admin_user_organization_role,
    admin_category,
    admin_folder,
    admin_document,
)
from core.roles import StaticRole
from schemas.role import RoleCreatePayload
from core.security import hash_password
from core.config import settings
from services.user_service import UserService
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
                
        admin_login = settings.ADMIN_LOGIN
        admin_password = settings.ADMIN_PASSWORD
        
        if admin_login == "" or admin_password == "":
            logging.warning("Admin credentials are not set. Please set ADMIN_LOGIN and ADMIN_PASSWORD in the .env file.")
        else:
            existing_admin = await UserService.get_user_by_username(db, admin_login)
            if not existing_admin:
                from models.user import User
                admin_user = User(
                    username=admin_login,
                    email=f"{admin_login}@local.com",
                    hashed_password=hash_password(admin_password),
                    is_active=True,
                    is_superuser=True,
                )
                await UserService.create_user(db, admin_user)
                logging.info(f"Admin user '{admin_login}' created.")
        
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.error(f"Unhandled exception for {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"})


@app.get("/status")
def get_status() -> dict[str, str]:
    return {"status": "ok"}


api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(category_router.router)
api_router.include_router(organization_router.router)
api_router.include_router(document_router.router)

api_router.include_router(admin_user.router)
api_router.include_router(admin_organization.router)
api_router.include_router(admin_department.router)
api_router.include_router(admin_role.router)
api_router.include_router(admin_user_organization_role.router)
api_router.include_router(admin_category.router)
api_router.include_router(admin_folder.router)
api_router.include_router(admin_document.router)

app.include_router(api_router)
