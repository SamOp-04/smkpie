# Base
FROM python:3.9-slim as base

WORKDIR /app
COPY requirements.txt .

# Builder
FROM base as builder
RUN pip install --user --no-cache-dir -r requirements.txt

# Production
FROM base
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]