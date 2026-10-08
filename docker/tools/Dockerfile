ARG DOCKER_PYTHON_VERSION=3.12

FROM python:${DOCKER_PYTHON_VERSION}-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MYPY_CACHE_DIR=/cache/mypy \
    RUFF_CACHE_DIR=/cache/ruff \
    COVERAGE_FILE=/cache/.coverage \
    PYTEST_ADDOPTS="-o cache_dir=/cache/pytest"

RUN adduser -D -u 1000 tools \
    && mkdir -p /app /cache \
    && chown tools:tools /app /cache

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

USER tools
