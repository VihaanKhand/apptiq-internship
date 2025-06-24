FROM python:3.13-slim-bookworm

WORKDIR /app

# Install system deps and uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    pip install uv && \
    rm -rf /var/lib/apt/lists/*

# Copy lockfiles and install Python deps
COPY ./backend/api/uv.lock ./backend/api/pyproject.toml ./
RUN uv sync --frozen && rm ./uv.lock ./pyproject.toml

# Copy everything else
COPY ./envs/backend.env /opt/.env
COPY ./backend/api /app/api
COPY ./backend/shared_mcp /app/shared_mcp

# Set env + entrypoint
ENV PYTHONPATH /app:$PYTHONPATH
ENTRYPOINT ["uv", "run", "fastapi", "run", "api/main.py", "--root-path=/api"]
