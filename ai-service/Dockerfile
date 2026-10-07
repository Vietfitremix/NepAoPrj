FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY prompts ./prompts
COPY scripts ./scripts
COPY tests ./tests
# Trên VPS: catalog đọc từ PostgreSQL (DATABASE_URL); thư mục data chỉ cần cho demo-cache.json
ENV DATA_DIR=/data ENABLE_DEV_ROUTES=false
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
