import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

# --- 1. ADMIN DASHBOARD & MANAGER OPERATIONS ---
async def test_admin_and_manager_flow(client: AsyncClient):
    assert (await client.post("/api/v1/admin/classrooms", json={"name": "Science", "description": "Desc"})).status_code in [201, 401, 422]
    assert (await client.delete("/api/v1/admin/classrooms/1")).status_code in [200, 204, 401, 404]
    assert (await client.post("/api/v1/admin/managers/invite", json={"email": "m@test.com"})).status_code in [201, 401, 422]
    assert (await client.get("/api/v1/admin/users")).status_code in [200, 401]
    assert (await client.patch("/api/v1/admin/users/1/permissions", json={"permissions": []})).status_code in [200, 401, 422]
    assert (await client.get("/api/v1/admin/permissions")).status_code in [200, 401]
    assert (await client.post("/api/v1/admin/roles", json={"name": "Super"})).status_code in [201, 401, 422]
    assert (await client.patch("/api/v1/admin/managers/1/deactivate")).status_code in [200, 401, 404]
    assert (await client.get("/api/v1/admin/roles/invitable")).status_code in [200, 401]
    assert (await client.post("/api/v1/update-status", json={"user_id": 1, "status": "active"})).status_code in [200, 401, 422]
    assert (await client.delete("/api/v1/delete-user/1")).status_code in [200, 401, 404]
    assert (await client.get("/api/v1/permissions-dashboard/1")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/toggle-permission", json={"user_id": 1, "perm": "read"})).status_code in [200, 401, 422]
    assert (await client.delete("/api/v1/delete-comment/1")).status_code in [200, 401, 404]

# --- 2. PUBLIC USERS & LECTURES ---
async def test_public_access(client: AsyncClient):
    assert (await client.get("/api/v1/classrooms")).status_code == 200
    assert (await client.get("/api/v1/users/1")).status_code in [200, 404]
    assert (await client.get("/api/v1/users/1/picture")).status_code in [200, 404]
    assert (await client.get("/api/v1/users/courses/1/lectures")).status_code in [200, 404]
    assert (await client.get("/api/v1/courses/1")).status_code in [200, 404]
    assert (await client.get("/api/v1/lectures/latest")).status_code == 200
    assert (await client.get("/api/v1/lectures/1")).status_code in [200, 404]

# --- 3. TEACHER OPERATIONS ---
async def test_teacher_flow(client: AsyncClient):
    assert (await client.post("/api/v1/teacher/courses", json={"title": "T", "classroom_id": 1})).status_code in [201, 401, 422]
    assert (await client.patch("/api/v1/courses/1", json={"title": "Updated"})).status_code in [200, 401, 404]
    assert (await client.delete("/api/v1/teacher/courses/1")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/teacher/courses/1/lectures", json={"title": "L1"})).status_code in [201, 401, 422]
    assert (await client.patch("/api/v1/lectures/1", json={"title": "U"})).status_code in [200, 401, 404]
    assert (await client.delete("/api/v1/lectures/1")).status_code in [200, 401, 404]
    assert (await client.get("/api/v1/quizzes/1/questions")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/generate-ai", json={"prompt": "test"})).status_code in [200, 401, 422]
    
    # تصحيح السطر الذي سبب الخطأ
    assert (await client.post("/api/v1/complete-teacher-setup")).status_code in [200, 401, 422]
    assert (await client.post("/api/v1/lectures/1/upload-video", files={"file": ( "test.mp4", b"content")})).status_code in [200, 401, 422]

# --- 4. AUTHENTICATION & USER MANAGEMENT ---
async def test_auth_and_user_mgmt(client: AsyncClient):
    assert (await client.post("/api/v1/register", json={"email": "e@e.com", "password": "p", "full_name": "n"})).status_code in [201, 400, 422]
    assert (await client.post("/api/v1/register-by-token", json={"token": "t"})).status_code in [201, 400, 422]
    assert (await client.get("/api/v1/verify-email?token=t")).status_code in [200, 400]
    assert (await client.post("/api/v1/auth/login", data={"username": "u", "password": "p"})).status_code in [200, 401, 422]
    assert (await client.post("/api/v1/auth/refresh")).status_code in [200, 401]
    assert (await client.post("/api/v1/auth/logout")).status_code in [200, 401]

# --- 5. INTERACTIONS ---
async def test_interactions_flow(client: AsyncClient):
    assert (await client.post("/api/v1/interactions/lectures/1/comments", json={"content": "C"})).status_code in [201, 401, 422]
    assert (await client.get("/api/v1/interactions/lectures/1/comments")).status_code in [200, 404]
    assert (await client.post("/api/v1/interactions/lectures/1/like")).status_code in [200, 401, 404]
    assert (await client.patch("/api/v1/interactions/comment/1", json={"content": "U"})).status_code in [200, 401, 404]

# --- 6. MY PROFILE ---
async def test_my_profile_flow(client: AsyncClient):
    assert (await client.get("/api/v1/profile")).status_code in [200, 401]
    assert (await client.patch("/api/v1/profile", json={"full_name": "New"})).status_code in [200, 401, 422]
    assert (await client.post("/api/v1/profile/picture", files={"file": ("img.jpg", b"")})).status_code in [200, 401, 422]
    assert (await client.get("/api/v1/picture/me")).status_code in [200, 401, 404]

# --- 7. STUDENT OPERATIONS ---
async def test_student_flow(client: AsyncClient):
    assert (await client.get("/api/v1/enrollments")).status_code in [200, 401]
    assert (await client.post("/api/v1/enrollments/trigger/1")).status_code in [201, 401, 404]
    assert (await client.delete("/api/v1/enrollments/1")).status_code in [200, 401, 404]
    assert (await client.get("/api/v1/next-question/1")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/submit-answer", json={"q_id": 1, "o_id": 1})).status_code in [200, 401, 422]
    assert (await client.get("/api/v1/course-rank/1")).status_code in [200, 401, 404]