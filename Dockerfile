FROM python:3.14-slim AS builder

# Install uv to manage dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

# Install dependencies into the system environment
# --frozen ensures we use the exact versions in uv.lock
# --no-install-project avoids installing the current project itself as a package
RUN uv sync --frozen --no-install-project

COPY . .

RUN mkdir -p /app/downloads

ENTRYPOINT ["uv", "run", "main.py"]

CMD ["--help"]
