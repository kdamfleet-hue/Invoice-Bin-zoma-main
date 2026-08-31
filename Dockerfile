FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=3000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=1001:1001 . .
RUN chmod +x start.sh \
    && if [ -f /app/ws_example_data.json ]; then cp -f /app/ws_example_data.json /app/routes/ws_example_data.json; fi \
    && chown -R 1001:1001 /app

EXPOSE 3000
CMD ["sh", "start.sh"]
