
import asyncio
from sqlmodel import SQLModel, Session, select
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
from src.models.VerificationTok  import VerificationToken
from src.models.Student_Mastery import Student_Mastery
from src.models.Department import Department
from src.core.dep import engine
Quiz_Attempt.model_rebuild()

from src.seed import initial_setup 


async def init_db_async():
    print("إنشاء الجداول ")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print(" تم إنشاء الجداول بنجاح.")

def create_db_and_seed():
    asyncio.run(init_db_async())

if __name__ == "__main__":
    create_db_and_seed()