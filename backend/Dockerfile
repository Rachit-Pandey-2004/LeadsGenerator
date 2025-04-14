FROM python:3.10-slim

# Install Rust (needed for aiograpi)
RUN apt update && \
    apt install -y curl build-essential gcc && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y

# Add Rust to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 \
    libxrandr2 libxdamage1 libxext6 libxfixes3 libx11-xcb1 libxcb1 \
    libx11-6 libasound2 libgbm1 libgtk-3-0 libxss1 libxshmfence1 wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install

COPY ./app /app

CMD ["python3", "main.py"]