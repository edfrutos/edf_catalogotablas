# Multi-stage Dockerfile for edf_catalogotablas
# Stage 1: Builder - compile dependencies
# Stage 2: Runtime - minimal production image

# ============================================================
# STAGE 1: Builder
# ============================================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create wheels for all dependencies
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ============================================================
# STAGE 2: Runtime
# ============================================================
FROM python:3.10-slim

ARG APP_ENV=production
ENV APP_ENV=$APP_ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pip wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install wheels (no build compilation needed)
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1001 -s /sbin/nologin appuser && \
    chown -R appuser:appuser /app

# Create directories for runtime data
RUN mkdir -p /app/logs /app/app/static/uploads && \
    chown -R appuser:appuser /app/logs /app/app/static/uploads

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Expose port
EXPOSE 5002

# Default command - use gunicorn for production
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5002", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "wsgi:app"]
