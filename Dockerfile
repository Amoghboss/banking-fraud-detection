# Sentinel Banking Fraud Detection - Production Docker Container
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . /app/

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/login || exit 1

# Start production server with Gunicorn
CMD ["gunicorn", "--workers", "4", "--threads", "2", "--bind", "0.0.0.0:5000", "wsgi:app"]
