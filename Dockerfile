FROM python:3.12.11-alpine3.22

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./monitoring /monitoring
RUN chmod +x /monitoring/run.sh
WORKDIR /monitoring
EXPOSE 8000

ARG DEV=false

# Install fping using Alpine's package manager
RUN apk add --no-cache fping

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
      build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

CMD ["/monitoring/run.sh"]