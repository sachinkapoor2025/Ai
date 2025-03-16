# Use Python base image
FROM python:3.9

# Install system dependencies for TA-Lib before installing Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libta-lib0 \
    ta-lib \
    && rm -rf /var/lib/apt/lists/*

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