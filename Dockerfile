# Use Playwright image (browsers included)
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Create app user & dir
ARG APP_DIR=/app
ENV APP_DIR=${APP_DIR}
WORKDIR ${APP_DIR}

# Keep logs unbuffered
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# System deps needed for PDF/image libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage layer cache
COPY requirements.txt ${APP_DIR}/requirements.txt

# Upgrade pip and install runtime deps
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r ${APP_DIR}/requirements.txt

# Create a non-root user for running the app
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser ${APP_DIR}

# Copy only runtime files (avoid tests and dev assets)
# Adjust list if your app needs additional files at runtime (e.g., templates)
COPY --chown=appuser:appuser main.py ${APP_DIR}/
# If your app needs to access any static or small data files at runtime, copy them explicitly:
# COPY --chown=appuser:appuser dummy_doc.pdf ${APP_DIR}/dummy_doc.pdf
# COPY --chown=appuser:appuser Dummy_CSV__sales_.csv ${APP_DIR}/Dummy_CSV__sales_.csv

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Healthcheck - uses the app's root endpoint
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://127.0.0.1:8080/ || exit 1

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
