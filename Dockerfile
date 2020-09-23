FROM python:3.8-slim-buster
WORKDIR /talks-api
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
COPY src src
COPY pyproject.toml poetry.lock ./
RUN pip install "poetry==1.0.10" && \
    poetry config virtualenvs.create false && \
    POETRY_VIRTUALENVS_CREATE=false poetry install --no-dev
CMD [ "poetry", "run", "python", "src/talks_api/main.py", "--port=8080" ]