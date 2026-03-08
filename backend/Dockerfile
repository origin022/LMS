FROM python:3.13-slim

# تثبيت curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod +x /install.sh && /install.sh && rm /install.sh

ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
COPY pyproject.toml ./

# مزامنة المكتبات بدون --frozen للسماح بإنشاء ملف قفل جديد وخفيف
RUN uv sync

COPY . .

# تشغيل الباك إند
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]