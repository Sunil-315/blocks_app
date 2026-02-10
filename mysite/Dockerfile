# Use the Python version matching your traceback
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /mysite

# Install system dependencies (for building some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY mysite/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project
COPY mysite/ /mysite/

# Collect static files at build time
RUN python manage.py collectstatic --noinput

# Expose the port Daphne will run on
EXPOSE 8000

# Run migrations at startup, then start Daphne
CMD python manage.py migrate --noinput && daphne -b 0.0.0.0 -p ${PORT:-8000} mysite.asgi:application