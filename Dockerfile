# 1. Use an official, lightweight Python base image
FROM python:3.11-slim

# 2. Prevent Python from writing .pyc files & buffer stdout/stderr for logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set working directory inside the container
WORKDIR /app

# 4. Install system dependencies required for psycopg2 / compiling C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy dependencies first to leverage Docker layer caching
COPY requirements.txt .

# 6. Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy project code into container
COPY . .

# 8. Expose port 8000 for FastAPI
EXPOSE 8000

# 9. Default command to start Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
