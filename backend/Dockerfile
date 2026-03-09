FROM python:3.13-slim

# 1. تثبيت المتطلبات
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. تثبيت uv بطريقة آمنة
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 3. عزل البيئة الافتراضية خارج مجلد التطبيق لتجنب مسحها عند ربط الفوليوم
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 4. نسخ ملفات التعريف والتثبيت
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project

# 5. نسخ الكود بالكامل وتثبيته
COPY . .
RUN uv sync --frozen

# 6. تعريف المسار البرمجي
ENV PYTHONPATH=/app/src
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]