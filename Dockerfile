FROM python:3.9.4-buster
USER root

ARG APP_ENV
ARG POETRY_VERSION
ENV APP_ENV=${APP_ENV:-develop} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=${POETRY_VERSION:-1.1.5}

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml ./

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
# ENV TERM xterm

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

RUN poetry config virtualenvs.create false \
    && poetry install $(test "$APP_ENV" == production && echo "--no-dev") --no-interaction --no-ansi
