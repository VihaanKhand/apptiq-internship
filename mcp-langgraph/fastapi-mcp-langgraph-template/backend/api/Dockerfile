FROM python:3.11-slim

WORKDIR /app

# Install system deps and uv
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    pip install uvicorn && \
    rm -rf /var/lib/apt/lists/*

# Copy lockfiles and install Python deps
COPY ./backend/api/pyproject.toml ./
RUN pip install --no-cache-dir . && rm pyproject.toml

# Copy everything else
COPY ./envs/backend.env /opt/.env
COPY ./backend/api /app/api
COPY ./backend/shared_mcp /app/shared_mcp

# Set env + entrypoint
ENV PYTHONPATH /app:$PYTHONPATH
ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--root-path=/api", "--reload"]