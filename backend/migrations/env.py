import asyncio
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

# 1. استيراد كائن الإعدادات الخاص بك (تأكد من المسار الصحيح)
from src.core.config import config as app_config

# 2. استيراد الموديلات (المهم جداً لـ autogenerate)
from sqlmodel import SQLModel
# الاستيرادات التي وضعتها أنت ضرورية لضمان تسجيلها في MetaData
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

# إعدادات ألمبيك
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def get_url():
    """جلب الرابط وتحويله من asyncpg إلى psycopg2 لعمل الهجرات"""
    url = str(app_config.SQLALCHEMY_DATABASE_URI)
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "+psycopg2")
    return url

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """تشغيل الهجرات في وضع الـ Online باستخدام محرك متزامن"""
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()