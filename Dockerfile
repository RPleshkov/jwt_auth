FROM python:3.13-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /auth_practice

RUN pip install --upgrade pip wheel "poetry==2.1.1"
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock* ./

RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "app/main.py"]