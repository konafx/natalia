FROM python:3.8.6
USER root

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml ./

# RUN apt update
# RUN apt -y install locales && \
    # localedef -f UTF-8 -i ja_JP ja_JP.UTF-8

# ENV LANG ja_JP.UTF-8
# ENV LANGUAGE ja_JP:ja
# ENV LC_ALL ja_JP.UTF-8
# ENV TZ JST-9
# ENV TERM xterm

# RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install