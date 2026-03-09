FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /install.sh
RUN sh /install.sh && rm /install.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock* ./

# --system تجعل uv يثبت المكتبات مباشرة في نظام الحاوية بدلاً من .venv
# وهذا يحل مشكلة "No such file or directory" تماماً
RUN uv sync --system --no-install-project

COPY . .

RUN uv sync --system

ENV PYTHONPATH=/app/src

# الآن uvicorn سيكون متاحاً في النظام مباشرة
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]