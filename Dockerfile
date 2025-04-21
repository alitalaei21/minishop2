FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set working directory
RUN mkdir "/app"
WORKDIR "/app"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Copy and make entrypoint scripts executable
COPY entrypoint.sh /app/entrypoint.sh
COPY celery-entrypoint.sh /app/celery-entrypoint.sh
COPY celery-beat-entrypoint.sh /app/celery-beat-entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/celery-entrypoint.sh /app/celery-beat-entrypoint.sh

# Expose port
EXPOSE 8000

# Default entrypoint and command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]