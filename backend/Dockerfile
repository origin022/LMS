FROM python:3.13-slim

# 1. تثبيت المتطلبات الأساسية و curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. تثبيت uv بأفضل طريقة رسمية
ADD https://astral.sh/uv/install.sh /install.sh
RUN sh /install.sh && rm /install.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

# 3. نسخ ملفات التعريف أولاً (Cache optimization)
# نسخ الـ lock file إذا موجود لضمان ثبات الإصدارات
COPY pyproject.toml uv.lock* ./

# 4. تثبيت المكتبات قبل نسخ الكود (عشان ما يعيد التثبيت كل ما عدلت سطر كود)
RUN uv sync --no-install-project

# 5. نسخ الكود بالكامل (بما فيه src و tests)
COPY . .

# 6. تثبيت المشروع نفسه
RUN uv sync

# 7. أهم خطوة: تعريف المسار البرمجي لـ FastAPI و Pytest
# بما أن ملفاتك داخل src/ فلازم الدوكر يشوفها
ENV PYTHONPATH=/app/src

# 8. تشغيل التطبيق
# ملاحظة: عدلت المسار ليكون src.main:app لأن ملفك داخل مجلد src
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]