# Python base image
FROM python:3.8-slim as base

# Python environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1

# Install global dependencies
RUN apt-get update && \
    apt-get upgrade -y


# Export dependencies from poetry
FROM base as export-dependencies

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy dependencies
COPY poetry.lock pyproject.toml ./

# Export to requirements format
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes


# Install dependencies
FROM base as dependencies

# Instlal build dependencies
RUN apt-get install -y --no-install-recommends build-essential git

# Install dependencies
COPY --from=export-dependencies /requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --prefix=/dependencies --no-warn-script-location


# Build the svelte frontend
FROM node:14-alpine as frontend

WORKDIR /frontend

# Install dependencies
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy over project files
COPY frontend/public ./public
COPY frontend/src ./src
COPY frontend/postcss.config.js ./
COPY frontend/rollup.config.js ./

# Build the project
RUN yarn build


# Build the common
FROM base as common

# Switch to a new user
RUN adduser --disabled-password app
USER app

WORKDIR /wafflebot

# Copy dependencies
COPY --from=dependencies /dependencies /usr/local

# Copy common project files
COPY --chown=app alembic ./alembic
COPY --chown=app common ./common
COPY --chown=app alembic.ini ./
COPY --chown=app manage.py ./


###
# Bot image
###
FROM common as bot

# Add project files
COPY --chown=app bot ./bot

# Startup configuration
COPY --chown=app --chmod=775 docker-entrypoints/bot.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]


###
# Web image
##
FROM common as web

# Add project files
COPY --chown=app --from=frontend /frontend/public ./frontend/public
COPY --chown=app api ./api
COPY --chown=app emojis.json ./

# Startup configuration
EXPOSE 8000
COPY --chown=app --chmod=775 docker-entrypoints/web.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
