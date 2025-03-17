# Use Python 3.13 with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /project

# Copy the pyproject.toml and uv.lock from the project root
COPY pyproject.toml uv.lock ./

# Create a virtual environment for the project 
RUN uv venv /project/.venv
ENV PATH="/project/.venv/bin:$PATH"

# Install dependencies using uv sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Install gunicorn for production
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install gunicorn

# Copy backend project files
WORKDIR /app
COPY backend/ .

# Expose port
EXPOSE 8000

# Add entrypoint script
COPY backend/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]