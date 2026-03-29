from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routers import profile as profile_router
from src.routers import users as users_router 
from src.routers import login as login_router
from src.routers import user as user_router
from src.routers import admin as admin_router
from src.routers import manager as manager_router
from src.routers import teacher as teacher_router
from src.routers import interaction as interaction_router
from src.routers import student as student_router
from src.routers import donation as donation_router
from src.models.Quiz_Attempt import Quiz_Attempt
from fastapi.middleware.cors import CORSMiddleware

Quiz_Attempt.model_rebuild()


app = FastAPI(
    title="LMS API",
    version="1.0.0",
    description="API for Learning Management System",



)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_origin_regex="http://localhost:.*",
    allow_methods=["*"],
    allow_headers=["*"],
)
import os
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")



app.include_router(
    admin_router.router,
        prefix="/api/v1",

    tags=["Admin Dashboard"]
)

app.include_router(
    users_router.router,
    prefix="/api/v1",
    tags=["Public Users"]
)
app.include_router(
    login_router.router,
    prefix="/api/v1",
    tags=["Authentication"]
)
app.include_router(
    user_router.router,
    prefix="/api/v1",
    tags=["user Management"]
)

app.include_router(
    interaction_router.router,
    prefix="/api/v1",  
    tags=["Interactions"]
)

app.include_router(
    profile_router.router,
    prefix="/api/v1", 
    tags=["My Profile"]
)
app.include_router(
    manager_router.router,
    prefix="/api/v1", 
    tags=["Manager Operations"] 
)

app.include_router(
    teacher_router.router,
    prefix="/api/v1", 
)
app.include_router(
    student_router.router,
    prefix="/api/v1",
)


app.include_router(
    donation_router.router,
    prefix="/api/v1",
    tags=["donation"]

)

