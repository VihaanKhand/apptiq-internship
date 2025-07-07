FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY uv.lock .
COPY . .

# Install dependencies using uv pip
RUN uv pip install --system --no-cache .

# Create AWS credentials folder (optional)
RUN mkdir -p /root/.aws

EXPOSE 5010

# Run FastAPI server
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5010"]