FROM python:3.9-slim

WORKDIR /app

COPY ./requirements/requirements.backend.txt .

RUN pip install -r requirements.backend.txt --no-cache-dir

COPY ./backend .
COPY data/ ../data

CMD ["sh", "entrypoint.sh"]