# Use an official Python 3.12 image to fully support Django 6.0.6
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed to compile C-binary packages (like psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and pull down standard deployment wheels
RUN pip install --no-cache-dir --upgrade pip wheel daphne

# Copy and install your consolidated requirements.txt file natively
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of your application code
COPY . /app/

# Expose Daphne's default port
EXPOSE 8000

# Run Daphne using your explicit core_logic module path
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core_logic.asgi:application"]
