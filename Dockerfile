# Create the file in the project root
# Path: ai-test-automation/Dockerfile

FROM python:3.10

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libxcb1 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p reports screenshots logs

# Expose the port
EXPOSE 8080

# Environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Command to run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app.app:app