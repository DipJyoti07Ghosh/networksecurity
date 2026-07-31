FROM python:3.10-slim

WORKDIR /app

# Set non-interactive mode to prevent debconf/tzdata prompts from breaking the build
ENV DEBIAN_FRONTEND=noninteractive

COPY . /app

# Combine update, install, and cache cleanup into a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    awscli \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "app.py"]