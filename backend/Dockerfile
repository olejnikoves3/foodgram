FROM python:3.9-slim

WORKDIR /app

COPY ./requirements/requirements.backend.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.backend.txt --no-cache-dir

COPY data/ ../data
COPY ./backend .

CMD ["sh", "entrypoint.sh"]