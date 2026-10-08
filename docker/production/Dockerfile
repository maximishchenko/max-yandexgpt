ARG DOCKER_PYTHON_VERSION=3.12
ARG DOCKER_APP_USER=bot
ARG DOCKER_APP_HOME=/home/bot

FROM python:${DOCKER_PYTHON_VERSION}-alpine AS builder

ARG DOCKER_APP_USER
ARG DOCKER_APP_HOME

ENV BUILD_DIR=/usr/src/app
WORKDIR $BUILD_DIR

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir $BUILD_DIR/wheels -r requirements.txt

FROM python:${DOCKER_PYTHON_VERSION}-alpine

ARG DOCKER_APP_USER
ARG DOCKER_APP_HOME

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/* \
    && rm -rf /wheels

RUN mkdir -p $DOCKER_APP_HOME
RUN addgroup -S $DOCKER_APP_USER && \
    adduser -S -D -h $DOCKER_APP_HOME -G $DOCKER_APP_USER $DOCKER_APP_USER

WORKDIR $DOCKER_APP_HOME

RUN chown -R $DOCKER_APP_USER:$DOCKER_APP_USER $DOCKER_APP_HOME
COPY --chown=$DOCKER_APP_USER:$DOCKER_APP_USER max_yandexgpt $DOCKER_APP_HOME/max_yandexgpt
COPY --chown=$DOCKER_APP_USER:$DOCKER_APP_USER bot.py $DOCKER_APP_HOME/bot.py

COPY docker/common/entrypoint.sh /usr/local/bin/entrypoint.sh

USER $DOCKER_APP_USER
ENTRYPOINT ["/bin/sh", "/usr/local/bin/entrypoint.sh"]
CMD ["python", "bot.py"]