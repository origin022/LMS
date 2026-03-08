"""seed_initial_data

Revision ID: ed278ab7d1bc
Revises: d25ebd6ec40a
Create Date: 2026-03-08 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# --- هذه هي الأسطر التي تنقصك ---
revision: str = 'ed278ab7d1bc'
down_revision: Union[str, None] = 'd25ebd6ec40a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
# ------------------------------
# البيانات التعريفية
REQUIRED_PERMISSIONS = ["Publish", "Like", "Comment", "Delete Comment", "Assign Quiz", "Add Teacher", "Delete user", "Add Manager", "Delete Manager",
                         "Change Permission","Manage Profile","create classroom","delete classroom","view users","view classrooms",
                         "Limiting permission","Ban User","Quiz attempt","show attempted quiz","manage corse","view enrollments"]
REQUIRED_ROLES = ["Admin", "Manager", "Teacher", "Student"]
REQUIRED_STATES = ["Active", "Pending", "Banned"]

ROLE_PERMISSIONS_MAP = {
    "Admin": ["Add Manager", "Delete Manager","Change Permission","create classroom","delete classroom","view users","view classrooms"],
    "Manager": ["Add Teacher", "Delete user", "Delete Comment","Limiting permission","Ban User","view users"],
    "Teacher": ["Publish", "Assign Quiz", "Comment", "Like","Manage Profile","show attempted quiz","manage corse"],
    "Student": ["Like", "Comment", "Manage Profile","Quiz attempt","view enrollments"],
}

def upgrade() -> None:
    conn = op.get_bind()

    # 1. إدخال الصلاحيات (مع تجنب التكرار)
    for perm in REQUIRED_PERMISSIONS:
        conn.execute(sa.text(f"INSERT INTO permission (name) SELECT '{perm}' WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name='{perm}')"))

    # 2. إدخال الحالات
    for state in REQUIRED_STATES:
        conn.execute(sa.text(f"INSERT INTO state (name) SELECT '{state}' WHERE NOT EXISTS (SELECT 1 FROM state WHERE name='{state}')"))

    # 3. إدخال الأدوار
    for role in REQUIRED_ROLES:
        conn.execute(sa.text(f"INSERT INTO roles (roles_name) SELECT '{role}' WHERE NOT EXISTS (SELECT 1 FROM roles WHERE roles_name='{role}')"))

    # 4. ربط الأدوار بالصلاحيات (Roles_Permission)
    for role_name, perms in ROLE_PERMISSIONS_MAP.items():
        for perm_name in perms:
            # استعلام لإدخال الربط بناءً على الأسماء لجلب الـ IDs ديناميكياً
            sql = sa.text("""
                INSERT INTO roles_permission (role_id, permission_id)
                SELECT r.roles_id, p.permission_id
                FROM roles r, permission p
                WHERE r.roles_name = :role_name AND p.name = :perm_name
                AND NOT EXISTS (
                    SELECT 1 FROM roles_permission rp 
                    WHERE rp.role_id = r.roles_id AND rp.permission_id = p.permission_id
                )
            """)
            conn.execute(sql, {"role_name": role_name, "perm_name": perm_name})

def downgrade() -> None:
    # يمكنك تركها فارغة أو كتابة أوامر Delete إذا أردت تنظيف البيانات عند التراجع
    pass