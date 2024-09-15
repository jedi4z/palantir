FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building TA-Lib and other packages
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    make \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download and build TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --build=aarch64-unknown-linux-gnu --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python main.py --tickers=$TICKERS --fetch-every=$FETCH_EVERY"]
