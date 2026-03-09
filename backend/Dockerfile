FROM python:3.13-slim

# 1. تثبيت المتطلبات
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. تثبيت uv
ADD https://astral.sh/uv/install.sh /install.sh
RUN sh /install.sh && rm /install.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

# 3. منع uv من إنشاء بيئة افتراضية داخل الحاوية 
# وإجبارها على التثبيت في المسار العام للحاوية بطريقة آمنة
ENV UV_PROJECT_ENVIRONMENT=/usr/local

# 4. نسخ ملفات التعريف والتثبيت
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project

# 5. نسخ الكود بالكامل وتثبيته
COPY . .
RUN uv sync --frozen

# 6. تعريف المسار البرمجي
ENV PYTHONPATH=/app/src

# الآن uvicorn سيكون متاحاً في /usr/local/bin تلقائياً
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]