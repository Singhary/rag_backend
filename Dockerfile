# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Prisma CLI globally
RUN npm install -g prisma

# Copy the entire application into the container
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Run Prisma generate and apply migrations
RUN prisma generate
RUN prisma migrate deploy

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
