FROM python:3.11-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn src.wsgi:application --bind 0.0.0.0:8000"]