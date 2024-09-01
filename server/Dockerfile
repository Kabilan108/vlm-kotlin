# Base image
FROM nvidia/cuda:12.6.0-devel-ubuntu22.04 AS base

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Dependencies stage
FROM base AS dependencies

WORKDIR /app

# Copy only pyproject.toml and uv.lock (if exists)
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv venv
RUN uv pip install torch==2.1.2 setuptools==74.0.0
RUN uv sync --frozen --no-cache

# Model stage
FROM dependencies AS model

# Copy only the necessary files for model download
COPY scripts/download_model.py /app/scripts/download_model.py

# Download models
RUN /app/.venv/bin/python scripts/download_model.py

# Final stage
FROM base

# Copy the application into the container
COPY . /app
WORKDIR /app

# Copy the virtual environment from the dependencies stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy the downloaded models from the model stage
COPY --from=model /models /app/models

# Set the environment variable to use GPU
ENV CUDA_VISIBLE_DEVICES=0

# Run the application
CMD ["/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
