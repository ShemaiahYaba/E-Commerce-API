# E-Commerce API – run with Uvicorn (ASGI)
FROM python:3.11-slim

WORKDIR /app

RUN useradd -m appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R appuser:appuser /app
USER appuser

ENV FLASK_ENV=production
ENV USE_UVICORN=1

EXPOSE 5000

CMD ["python", "-m", "uvicorn", "run:asgi_app", "--host", "0.0.0.0", "--port", "5000"]
