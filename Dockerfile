# المرحلة الأولى: بناء التبعيات (Build Stage)
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# استخدام البيئة الوهمية (Virtual Environment) لضمان توافق المسارات لكل المستخدمين
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# المرحلة الثانية: التشغيل (Final Stage)
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ البيئة الوهمية بالكامل من مرحلة البناء
COPY --from=builder /opt/venv /opt/venv
# تفعيل البيئة الوهمية بشكل افتراضي
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

# ضبط إعدادات الأمان والتخزين المؤقت عبر متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# أمر التشغيل الاحترافي (استخدام sh -c لضمان تقييم $PORT بشكل سليم في كل بيئات لينكس)
CMD ["sh", "-c", "gunicorn --workers 2 --threads 4 --worker-class gevent --worker-tmp-dir /dev/shm --bind 0.0.0.0:$PORT app:app"]
