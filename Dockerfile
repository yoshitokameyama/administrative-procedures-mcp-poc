FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    MCP_NO_UI=1 \
    ADMIN_PROCEDURES_HOST=0.0.0.0 \
    ADMIN_PROCEDURES_REQUIRE_AUTH=1 \
    ADMIN_PROCEDURES_DATA_DIR=/app \
    ADMIN_PROCEDURES_TRANSPORT=streamable-http \
    ADMIN_PROCEDURES_PATH=/mcp \
    PORT=8000

COPY pyproject.toml uv.lock README.md LICENSE NOTICE ./
COPY src ./src
COPY datasets ./datasets

RUN uv sync --frozen --no-dev --extra excel \
    && uv run apcli fetch procedures-survey-r6 \
    && rm -rf source-data \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

EXPOSE 8000

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
    CMD [".venv/bin/python", "-c", "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/health', timeout=3)"]

CMD [".venv/bin/python", "-m", "admin_procedures"]
