# Production Dockerfile for Railway
FROM python:3.10-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# System dependencies
# (None currently needed for pure Python logic)

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY main.py /app/main.py

# Expose port and run
EXPOSE 8080
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]