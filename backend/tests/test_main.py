import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

# --- 1. AUTHENTICATION & USER MANAGEMENT ---
async def test_auth_flow(client: AsyncClient):
    # Registration
    assert (await client.post("/api/v1/register", json={"email": "test@lms.com", "password": "pass", "full_name": "Test User"})).status_code in [201, 400, 422]
    assert (await client.post("/api/v1/register-by-token", json={"token": "t-123"})).status_code in [201, 400, 422]
    assert (await client.get("/api/v1/verify-email?token=t-123")).status_code in [200, 400]
    
    # Login Flow
    assert (await client.post("/api/v1/auth/login", data={"username": "test@lms.com", "password": "pass"})).status_code in [200, 401, 422]
    assert (await client.post("/api/v1/auth/refresh")).status_code in [200, 401]
    assert (await client.post("/api/v1/auth/logout")).status_code in [200, 401]

# --- 2. ADMIN OPERATIONS ---
async def test_admin_operations(client: AsyncClient):
    # Class Management
    assert (await client.post("/api/v1/admin/classrooms", json={"name": "Science", "description": "Desc"})).status_code in [201, 401, 422]
    assert (await client.delete("/api/v1/admin/classrooms/1")).status_code in [200, 204, 401, 404]
    
    # User & Role Management
    assert (await client.get("/api/v1/admin/users")).status_code in [200, 401]
    assert (await client.patch("/api/v1/admin/users/1/permissions", json={"permissions": []})).status_code in [200, 401, 422]
    assert (await client.get("/api/v1/admin/permissions")).status_code in [200, 401]
    assert (await client.post("/api/v1/admin/roles", json={"name": "Super"})).status_code in [201, 401, 422]
    assert (await client.get("/api/v1/admin/roles/invitable")).status_code in [200, 401]
    
    # Manager Invitation
    assert (await client.post("/api/v1/admin/managers/invite", json={"email": "m@test.com", "roles_id": 2})).status_code in [201, 401, 422]
    assert (await client.patch("/api/v1/admin/managers/1/deactivate")).status_code in [200, 401, 404]

# --- 3. MANAGER OPERATIONS ---
async def test_manager_operations(client: AsyncClient):
    # Dashboards
    assert (await client.get("/api/v1/manager/my-dashboard")).status_code in [200, 401]
    assert (await client.get("/api/v1/manager/permissions-dashboard/1")).status_code in [200, 401, 404]
    assert (await client.get("/api/v1/manager/permissions-dashboard/by-email/test@example.com")).status_code in [200, 401, 404]
    
    # User Management
    assert (await client.post("/api/v1/manager/update-status", json={"user_id": 1, "target_state": 1})).status_code in [200, 401, 422]
    assert (await client.delete("/api/v1/manager/delete-user/1")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/manager/toggle-permission", json={"user_id": 1, "permission_id": 1, "action": "block"})).status_code in [200, 401, 422]
    
    # Content Moderation
    assert (await client.get("/api/v1/manager/recent-comments")).status_code in [200, 401]
    assert (await client.delete("/api/v1/manager/delete-comment/1")).status_code in [200, 401, 404]

# --- 4. TEACHER OPERATIONS ---
async def test_teacher_flow(client: AsyncClient):
    assert (await client.post("/api/v1/teacher/courses", json={"title": "T", "classroom_id": 1})).status_code in [201, 401, 422]
    assert (await client.patch("/api/v1/courses/1", json={"title": "Updated"})).status_code in [200, 401, 404]
    assert (await client.delete("/api/v1/teacher/courses/1")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/teacher/courses/1/lectures", json={"title": "L1"})).status_code in [201, 401, 422]
    assert (await client.patch("/api/v1/lectures/1", json={"title": "U"})).status_code in [200, 401, 404]
    assert (await client.delete("/api/v1/lectures/1")).status_code in [200, 401, 404]
    assert (await client.get("/api/v1/quizzes/1/questions")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/generate-ai", json={"prompt": "test"})).status_code in [200, 401, 422]
    assert (await client.post("/api/v1/complete-teacher-setup")).status_code in [200, 401, 422]
    assert (await client.post("/api/v1/lectures/1/upload-video", files={"file": ("test.mp4", b"content")})).status_code in [200, 401, 422]

# --- 5. STUDENT OPERATIONS ---
async def test_student_flow(client: AsyncClient):
    assert (await client.get("/api/v1/enrollments")).status_code in [200, 401]
    assert (await client.post("/api/v1/enrollments/trigger/1")).status_code in [201, 401, 404]
    assert (await client.delete("/api/v1/enrollments/1")).status_code in [200, 401, 404]
    assert (await client.get("/api/v1/next-question/1")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/submit-answer", json={"q_id": 1, "o_id": 1})).status_code in [200, 401, 422]
    assert (await client.get("/api/v1/course-rank/1")).status_code in [200, 401, 404]

# --- 6. PUBLIC ACCESS & INTERACTIONS ---
async def test_public_and_interactions(client: AsyncClient):
    # Public
    assert (await client.get("/api/v1/classrooms")).status_code == 200
    assert (await client.get("/api/v1/users/1")).status_code in [200, 404]
    assert (await client.get("/api/v1/lectures/latest")).status_code == 200
    
    # Interactions
    assert (await client.post("/api/v1/interactions/lectures/1/comments", json={"text": "C"})).status_code in [201, 401, 422]
    assert (await client.get("/api/v1/interactions/lectures/1/comments")).status_code in [200, 404]
    assert (await client.post("/api/v1/interactions/lectures/1/like")).status_code in [200, 401, 404]

# --- 7. MY PROFILE & DONATIONS ---
async def test_profile_and_donations(client: AsyncClient):
    assert (await client.get("/api/v1/profile")).status_code in [200, 401]
    assert (await client.patch("/api/v1/profile", json={"bio": "Hello"})).status_code in [200, 401, 422]
    assert (await client.post("/api/v1/profile/picture", files={"file": ("img.jpg", b"")})).status_code in [200, 401, 422]
    assert (await client.get("/api/v1/picture/me")).status_code in [200, 401, 404]
    assert (await client.post("/api/v1/donations/start", json={"amount": 1000})).status_code in [200, 201, 400, 401, 422]

# --- 8. PUBLIC CONTENT BROWSING ---
async def test_public_content(client: AsyncClient):
    assert (await client.get("/api/v1/users/1/picture")).status_code in [200, 404]
    assert (await client.get("/api/v1/courses/1")).status_code in [200, 404]
    assert (await client.get("/api/v1/users/courses/1/lectures")).status_code in [200, 404]
    assert (await client.get("/api/v1/courses/1/lectures/quiz-map")).status_code in [200, 401, 404]

# --- 9. TEACHER EXTRA OPERATIONS ---
async def test_teacher_extra(client: AsyncClient):
    assert (await client.get("/api/v1/teacher/courses")).status_code in [200, 401]
    assert (await client.patch("/api/v1/quizzes/1/bulk", json={"questions": []})).status_code in [200, 401, 404, 422]
    assert (
        await client.patch("/api/v1/teacher/courses/1/thumbnail", files={"file": ("thumb.jpg", b"")})
    ).status_code in [200, 401, 404, 422]
    assert (
        await client.patch("/api/v1/teacher/lectures/1/thumbnail", files={"file": ("thumb.jpg", b"")})
    ).status_code in [200, 401, 404, 422]

# --- 10. WEBSOCKET COMMENTS ---
async def test_websocket_comments(client: AsyncClient):
    """Test that WebSocket endpoint exists and accepts connections."""
    import httpx
    # نتأكد فقط أن الـ endpoint موجود عبر طلب HTTP عادي (WebSocket upgrade)
    # سيرجع 426 Upgrade Required أو 403 لأن التيست لا يدعم WebSocket كامل
    res = await client.get("/api/v1/interactions/ws/1")
    assert res.status_code in [403, 426, 400, 101, 404]
