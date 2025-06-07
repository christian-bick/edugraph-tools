FROM ghcr.io/astral-sh/uv:python3.13-alpine

ARG APP_DIR="/usr/src/app"
ARG PORT=8080
ENV PORT=${PORT}
ARG ONTOLOGY_VERSION=0.1.0

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \

    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.8.3

# Copy only requirements to cache them in docker layer
WORKDIR ${APP_DIR}
COPY uv.lock pyproject.toml ${APP_DIR}

# Project initialization:
RUN uv sync --locked

# Creating folders, and files for a project:
COPY app.py .env* ${APP_DIR}
COPY /api ${APP_DIR}/api/
COPY /semantic ${APP_DIR}/semantic/

RUN wget https://github.com/christian-bick/edugraph-ontology/releases/download/${ONTOLOGY_VERSION}/core-ontology.rdf
RUN wget https://github.com/christian-bick/edugraph-ontology/releases/download/${ONTOLOGY_VERSION}/core-ontology.ttl

EXPOSE ${PORT}

CMD ["sh", "-c", "uv run waitress-serve --port=$PORT --call 'api:create_app'"]