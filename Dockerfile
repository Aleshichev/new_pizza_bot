FROM python:3.10-slim

#RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY . /app

COPY .env /app/

CMD ["python3", "app.py"]