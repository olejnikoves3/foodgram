FROM python:3.9

WORKDIR /app

COPY ./requirements/requirements.backend.txt .

RUN pip install -r requirements.backend.txt --no-cache-dir

COPY ./backend .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]