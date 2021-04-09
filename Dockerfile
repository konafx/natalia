FROM python:3.9.4-buster
USER root

ARG APP_ENV
ENV APP_ENV=${APP_ENV:-develop} \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY requirements.txt requirements.txt

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
# ENV TERM xterm

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
