FROM python:3.9-slim
EXPOSE 8080
WORKDIR app

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .
CMD ["streamlit", "run", "Top_page.py", "--server.port", "8080"]