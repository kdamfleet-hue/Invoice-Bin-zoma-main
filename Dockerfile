FROM python:3.12-slim

# ضبط إعدادات بايثون
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# إنشاء مستخدم عادي
RUN useradd -m appuser

WORKDIR /app

# تحديث pip أولاً
RUN pip install --no-cache-dir --upgrade pip

# نسخ المتطلبات
COPY requirements.txt .

# تثبيت الحزم (تجاهل تحذير الروت هنا لأننا في دوكر، أو يمكن تثبيتها بصلاحيات روت)
# يمكنك استخدام بيئة وهمية أو --user لتفادي تحذير pip لكن هذا يفي بالغرض حالياً
RUN pip install --no-cache-dir -r requirements.txt

# نسخ التطبيق وإعطاء الصلاحية للمستخدم العادي (مهم لقاعدة بيانات sqlite)
COPY . .
RUN chown -R appuser:appuser /app

# متغيرات البيئة الأساسية
ENV PORT=3000
ENV SECRET_KEY=Khaled@Damfleet1105090615
ENV ADMIN_USERNAME=Khaled@fleetadmin
ENV MASTER_PASSWORD=Khaled@Damfleet1105090615

EXPOSE 3000

# تبديل للمستخدم العادي
USER appuser

# تشغيل التطبيق مع الإعدادات المحسنة
# يجب أن يكون worker واحد فقط (1) لتفادي تعارضات قاعدة البيانات (SQLite) مع threading.Lock()
CMD ["sh", "-c", "gunicorn --workers 1 --threads 16 --bind 0.0.0.0:$PORT app:app"]
