FROM python:3.12-slim as compiler

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install -Ur requirements.txt

################################################################################
FROM python:3.12-slim as runner

WORKDIR /app

COPY --from=compiler /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /app
ENV PORT=5000
EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]