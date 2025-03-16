# Use Python base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project including tpqoa package
COPY . .

# Install tpqoa from local directory
RUN pip install ./tpqoa

# Install AWS Lambda Runtime Interface Client
RUN pip install --no-cache-dir awslambdaric

# Set Lambda entry point
CMD ["python", "-m", "awslambdaric", "main.lambda_handler"]