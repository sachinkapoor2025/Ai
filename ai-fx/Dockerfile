# Use Python base image
FROM python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Download and build TA-Lib manually
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -O /tmp/ta-lib.tar.gz \
    && tar -xzf /tmp/ta-lib.tar.gz -C /tmp/ \
    && cd /tmp/ta-lib-0.4.0/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && rm -rf /tmp/ta-lib*
    
# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip  # Ensure pip is updated
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project including tpqoa package
COPY . .

# Install tpqoa from local directory
RUN pip install ./tpqoa

# Install AWS Lambda Runtime Interface Client
RUN pip install --no-cache-dir awslambdaric

# Set Lambda entry point
CMD ["python", "-m", "awslambdaric", "main.lambda_handler"]