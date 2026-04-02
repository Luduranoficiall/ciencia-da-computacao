FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY platform/requirements.txt platform/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY platform/app ./app
COPY platform/static ./static
COPY data ./data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
