FROM python:3.13-slim-bookworm

# Set up working directory
WORKDIR /app

# Install curl + uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    pip install uv && \
    rm -rf /var/lib/apt/lists/*

# Copy and sync project
COPY ./backend/mcp/uv.lock ./backend/mcp/pyproject.toml .
RUN uv sync --frozen && rm ./uv.lock ./pyproject.toml

# Rest of your build
COPY ./backend/mcp ./mcp
COPY ./backend/shared_mcp ./shared_mcp
ENV PYTHONPATH /app:$PYTHONPATH
ENTRYPOINT ["uv", "run", "mcp/main.py"]
