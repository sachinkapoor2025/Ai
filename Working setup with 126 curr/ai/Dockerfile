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

# Command to run the bot
CMD ["python", "main.py"]