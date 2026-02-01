FROM python:3.10-slim

WORKDIR /app

COPY requirements.lock ./requirements.lock
COPY vendor/wheels ./vendor/wheels

RUN if [ -d "vendor/wheels" ] && [ "$(ls -A vendor/wheels 2>/dev/null)" ]; then \
      pip install --no-cache-dir --no-index --find-links vendor/wheels -r requirements.lock; \
    else \
      pip install --no-cache-dir -r requirements.lock; \
    fi

COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
