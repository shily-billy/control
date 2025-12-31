FROM python:3.11-slim

WORKDIR /app

# System deps for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install --with-deps chromium

COPY . /app

EXPOSE 8000
