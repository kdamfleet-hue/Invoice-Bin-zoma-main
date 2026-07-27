FROM python:3.12-slim

# Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and set permissions
COPY . .
RUN chown -R appuser:appuser /app

# Environment defaults
ENV PORT=3000

EXPOSE 3000

# Switch to non-root user
USER appuser

# Production Gunicorn: 3 workers + 2 threads each (gthread) for high concurrency
# PostgreSQL is used in production so multi-worker is safe
CMD ["sh", "start.sh"]
