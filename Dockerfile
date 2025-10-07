# Use the official Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt /app/
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy project files
COPY ./client /app/client
COPY ./controller /app/controller
COPY ./service /app/service
COPY ./static /app/static
COPY ./utility /app/utility
COPY ./main.py /app/main.py

# Expose port (FastAPI default is 8000)
EXPOSE 80

CMD ["python", "main.py"]