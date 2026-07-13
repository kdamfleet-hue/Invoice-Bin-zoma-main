# المرحلة الأولى: بناء التبعيات (Build Stage)
FROM python:3.12-slim AS builder

# تثبيت أدوات البناء الضرورية
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ ملف المتطلبات فقط لتثبيته (يستفيد من Docker Cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# المرحلة الثانية: التشغيل (Final Stage)
FROM python:3.12-slim

# تثبيت المكتبات الأساسية فقط وقت التشغيل
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ التبعيات المثبتة من مرحلة البناء
COPY --from=builder /root/.local /root/.local
COPY . .

# إضافة المسار للمكتبات المثبتة
ENV PATH=/root/.local/bin:$PATH

# ضبط إعدادات الأمان والتخزين المؤقت عبر متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# أمر التشغيل الاحترافي
ENV PORT=5000
CMD gunicorn --workers 2 --threads 4 --worker-class gevent --worker-tmp-dir /dev/shm --bind 0.0.0.0:$PORT app:app
