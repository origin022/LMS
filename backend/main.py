from fastapi import FastAPI
from src.routers import profile as profile_router
from src.routers import users as users_router 
from src.routers import login as login_router
from src.routers import user as user_router
from src.routers import admin as admin_router

from src.routers import interaction as interaction_router

app = FastAPI(
    title="LMS API",
    version="1.0.0",
    description="API for Learning Management System",
)
app.include_router(
    admin_router.router,
    tags=["Admin Dashboard"]
)

app.include_router(
    users_router.router,
    prefix="/api/v1/users",
    tags=["Public Users"]
)
app.include_router(
    login_router.router,
    prefix="/api/v1",
    tags=["Authentication"]
)
app.include_router(
    user_router.router,
    prefix="/api/v1/user",
    tags=["user Management"]
)

app.include_router(
    interaction_router.router,
    prefix="/api/v1",  
    tags=["Interactions"]
)

app.include_router(
    profile_router.router,
    prefix="/api/v1/profile", 
    tags=["My Profile"]
)
