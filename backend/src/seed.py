import asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.State import State
from src.models.Roles_Permission import Roles_Permission
from src.models.Roles import Roles
from src.models.Permission import Permission
from src.models.User_Permission import User_Permission 
from src.core.dep import engine

REQUIRED_PERMISSIONS = ["Publish", "Like", "Comment", "Delete Comment", "Assign Quiz", "Add Teacher", "Delete user", "Add Manager", "Delete Manager",
                         "Change Permission","Manage Profile","create classroom","delete classroom","view users","view classrooms",
                         "Limiting permission","Ban User","Quiz attempt","show attempted quiz","manage corse"]
REQUIRED_ROLES = ["Super Admin", "Manager", "Teacher", "Student"]
REQUIRED_STATES = ["Active", "Pending", "Banned"]
ROLE_PERMISSIONS_MAP = {
    "Super Admin": ["Add Manager", "Delete Manager","Change Permission","create classroom","delete classroom","view users","view classrooms"],
    "Manager": ["Add Teacher", "Delete user", "Delete Comment","Limiting permission","Ban User","view users"],
    "Teacher": ["Publish", "Assign Quiz", "Comment", "Like","Manage Profile","show attempted quiz","manage corse"],
    "Student": ["Like", "Comment", "Manage Profile","Quiz attempt"],
}

async def initial_setup():
    print(" بدء عملية تهيئة البيانات")
    async with AsyncSession(engine) as session:
        for perm_name in REQUIRED_PERMISSIONS:
            res = await session.exec(select(Permission).where(Permission.name == perm_name))
            if not res.first():
                session.add(Permission(name=perm_name))
                print(f"[Permissions] Added: {perm_name}")

        for state_name in REQUIRED_STATES:
            res = await session.exec(select(State).where(State.name == state_name))
            if not res.first():
                session.add(State(name=state_name))
                print(f"[States] Added: {state_name}")

        for role_name in REQUIRED_ROLES:
            res = await session.exec(select(Roles).where(Roles.roles_name == role_name))
            if not res.first():
                session.add(Roles(roles_name=role_name))
                print(f"[Roles] Added: {role_name}")

        await session.commit() 
        
        roles_res = await session.exec(select(Roles))
        perms_res = await session.exec(select(Permission))
        
        role_map = {r.roles_name: r for r in roles_res.all()}
        perm_map = {p.name: p for p in perms_res.all()}

        for role_name, perm_list in ROLE_PERMISSIONS_MAP.items():
            role_obj = role_map.get(role_name)
            for p_name in perm_list:
                perm_obj = perm_map.get(p_name)
                if role_obj and perm_obj:
                    check_link = await session.exec(
                        select(Roles_Permission).where(
                            Roles_Permission.role_id == role_obj.roles_id,
                            Roles_Permission.permission_id == perm_obj.permission_id
                        )
                    )
                    if not check_link.first():
                        session.add(Roles_Permission(role_id=role_obj.roles_id, permission_id=perm_obj.permission_id))
                        print(f"[Link] Linked: {role_name} -> {p_name}")

        await session.commit()
    print(" تمت العملية بنجاح  ")

if __name__ == "__main__":
    asyncio.run(initial_setup())