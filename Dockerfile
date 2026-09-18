# Multi-stage Python 3.13 Dockerfile for FastAPI Resume Analyzer API
FROM python:3.13-slim as builder

WORKDIR /app

# Install system dependencies needed for compiling C extensions & spaCy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Download spaCy model
RUN python -m pip install --no-cache-dir spacy && \
    python -m spacy download en_core_web_sm

# Final runtime image
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local
COPY --from=builder /root/.cache /root/.cache

# Copy application code
COPY . .

# Ensure uploads directory exists
RUN mkdir -p /app/uploads

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
