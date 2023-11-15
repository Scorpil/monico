FROM python:3.11-alpine

RUN apk add libffi-dev libpq-dev gcc musl-dev
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "-m", "monic" ]