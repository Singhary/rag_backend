FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN npx prisma generate
RUN npx prisma migrate deploy

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
