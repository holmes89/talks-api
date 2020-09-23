FROM python:3.8-slim-buster
WORKDIR /talks-api
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ADD src src
ADD pyproject.toml .
ADD poetry.lock .
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*  && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python && \
    poetry install
CMD [ "poetry", "run", "python", "src/talks_api/main.py" ]