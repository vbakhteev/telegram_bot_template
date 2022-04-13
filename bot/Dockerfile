FROM python:3.9

RUN pip install -U pip
RUN pip install poetry

WORKDIR /bot

COPY poetry.lock pyproject.toml /bot/
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

COPY . .

CMD python bot.py