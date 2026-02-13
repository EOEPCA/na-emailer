FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY app /app/app
COPY templates /app/templates

#install runtime deps (no venv inside container)
RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir .

ENV PORT=8080
EXPOSE 8080

CMD ["functions-framework", "--target", "handle", "--port", "8080"]
