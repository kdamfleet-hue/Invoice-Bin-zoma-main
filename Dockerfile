# مرحلة البناء (Builder)
FROM python:3.12-slim AS builder

WORKDIR /app

# تثبيت متطلبات النظام الضرورية للبناء
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# مرحلة التشغيل النهائية (Runtime)
FROM python:3.12-slim

WORKDIR /app

# تثبيت المكتبات الأساسية للتشغيل وإنشاء مستخدم غير جذر (non-root) للأمان
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r app && useradd -r -g app app

# نسخ البيئة وحزم البايثون من مرحلة البناء
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# نسخ كود التطبيق
COPY . .

# منح الصلاحيات للمستخدم الآمن
RUN chown -R app:app /app && chmod -R 755 /app

USER app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--workers", "2", "--threads", "4", "--worker-class", "gevent", \
     "--worker-tmp-dir", "/dev/shm", \
     "--log-level", "info", "app:app"]
