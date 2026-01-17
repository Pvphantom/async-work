FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for Postgres
RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .