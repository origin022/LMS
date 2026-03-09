import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from sqlmodel import SQLModel

from src.models.Roles import Roles
from src.models.User import User
from src.models.Like import Like
from src.models.Roles_Permission import Roles_Permission
from src.models.Permission import Permission
from src.models.Class_Manager import Class_Manager
from src.models.Teacher_Assignment import Teacher_Assignment
from src.models.Classroom import Classroom
from src.models.Comment import Comment
from src.models.Course import Course
from src.models.Lecture import Lecture
from src.models.Media import Media
from src.models.Profile import Profile
from src.models.Question import Question
from src.models.Quiz_Attempt import Quiz_Attempt
from src.models.Question_Option import Question_Option
from src.models.State import State
from src.models.Quiz import Quiz
from src.models.Enrollment import Enrollment
from src.models.User_Permission import User_Permission
from src.models.Invitation import Invitation
from src.models.VerificationTok import VerificationToken
from src.models.Student_Mastery import Student_Mastery

# الإعدادات الأساسية
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# الربط الصحيح للميتاداتا
target_metadata = SQLModel.metadata

# الرابط الثابت للدوكر
DATABASE_URL = "postgresql+asyncpg://postgres:12345@db:5432/lms"
config.set_main_option("sqlalchemy.url", DATABASE_URL)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # في بيئة الدوكر يفضل استخدام run_sync أو التأكد من الـ loop
        asyncio.run(run_async_migrations())
    else:
        asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()