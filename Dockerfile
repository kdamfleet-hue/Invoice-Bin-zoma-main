# --- المرحلة الأولى: التحضير (Builder) ---
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    pip install --no-cache-dir --upgrade pip uv

COPY requirements.txt .
RUN uv pip install --no-cache --system -r requirements.txt

# --- المرحلة الثانية: التشغيل (Runner) ---
FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# نسخ المكتبات المثبتة فقط من المرحلة الأولى
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# ضبط إعدادات الأمان والتخزين المؤقت عبر متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=3000
ENV SECRET_KEY=Khaled@Damfleet1105090615
ENV ADMIN_USERNAME=Khaled@fleetadmin
ENV MASTER_PASSWORD=Khaled@Damfleet1105090615

EXPOSE 3000
CMD ["sh", "-c", "gunicorn --workers 2 --threads 4 --worker-class gevent --worker-tmp-dir /dev/shm --bind 0.0.0.0:$PORT app:app"]
