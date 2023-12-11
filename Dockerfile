FROM python:3.11-alpine

RUN apk add libffi-dev libpq-dev gcc musl-dev
WORKDIR /usr/src/app
# TODO: install requirements first
COPY . .
RUN pip install '.[postgres]'


ENTRYPOINT [ "python", "-m", "monico" ]