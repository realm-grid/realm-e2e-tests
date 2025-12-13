# E2E Test Runner with Playwright and Behave
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

LABEL maintainer="Realm Grid Team"
LABEL description="E2E Test Runner for SSO Authentication Testing"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HEADLESS=true
ENV BROWSER=chromium

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy test files
COPY . .

# Create reports directory
RUN mkdir -p /app/reports/screenshots

# Default command runs auth tests
CMD ["behave", "features/auth/", "--tags=@sso,@smoke", "--no-capture", "-v"]
