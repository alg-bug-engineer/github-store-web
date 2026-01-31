FROM python:latest

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose health check port
EXPOSE 8001

# Default command (health check API)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
