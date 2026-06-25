# 📚 Al-Jahiz LMS

A full-stack **Learning Management System** built with **FastAPI** and **SvelteKit**, featuring role-based access control, AI-powered quiz generation, and a modern responsive UI.

## ✨ Features

- **Role-Based Access** — Admin, Manager, Teacher, and Student roles with granular permissions
- **Course Management** — Create courses, lectures, and classrooms with media uploads
- **AI Quiz Generation** — Auto-generate quizzes from lecture content using Groq AI
- **Student Tracking** — Enrollment management, quiz attempts, and mastery tracking
- **Interactions** — Comments and likes on lectures
- **Donation System** — Built-in donation support
- **Email Verification** — Secure registration with email confirmation
- **Rate Limiting** — API protection via SlowAPI

## 🛠 Tech Stack

| Layer        | Technology                              |
| ------------ | --------------------------------------- |
| **Backend**  | FastAPI · SQLModel · PostgreSQL · Alembic |
| **Frontend** | SvelteKit · TypeScript · TailwindCSS v4  |
| **AI**       | Groq API                                |
| **DevOps**   | Docker · Docker Compose                  |

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- (Or) Python 3.13+ & Node.js 18+

### Using Docker (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/your-username/LMS.git
cd LMS

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your values

# 3. Run
docker compose up --build
```

The app will be available at:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Manual Setup

<details>
<summary>Backend</summary>

```bash
cd backend
pip install uv
uv sync
alembic upgrade head    # run migrations
uvicorn main:app --reload
```
</details>

<details>
<summary>Frontend</summary>

```bash
cd frontend
npm install
npm run dev
```
</details>

## 📁 Project Structure

```
LMS/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── src/
│   │   ├── models/          # SQLModel database models
│   │   ├── routers/         # API route handlers
│   │   ├── services/        # Business logic
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── core/            # Config & security
│   │   └── templates/       # Email templates
│   └── db_migrations/       # Alembic migrations
├── frontend/
│   └── src/
│       ├── routes/          # SvelteKit pages
│       └── lib/             # Shared utilities & API client
├── docker-compose.yml
└── .env.example
```

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable         | Description              |
| ---------------- | ------------------------ |
| `SECRET_KEY`     | JWT signing key          |
| `POSTGRES_PASSWORD` | Database password     |
| `GROQ_API_KEY`   | Groq AI API key          |
| `MAIL_USERNAME`  | SMTP email address       |
| `MAIL_PASSWORD`  | SMTP app password        |

## 📄 License

This project is for educational purposes.
