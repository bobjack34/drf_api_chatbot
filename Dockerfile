FROM python:3.12-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

ENV PATH="opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/
COPY ./pyproject.toml ./uv.lock ./

RUN --mount=type=cache,target=/root/.cache \
    uv sync --frozen --no-install-project


COPY ./app ./

COPY ./app/entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

RUN useradd -m myuser \
    && mkdir -p /usr/src/app/staticfiles \
    && chown -R myuser:myuser /usr/src/app/staticfiles \
    && chown -R myuser:myuser /usr/src/app/data

USER myuser

ENTRYPOINT ["./entrypoint.sh"]
