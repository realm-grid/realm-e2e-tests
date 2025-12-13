# Playwright E2E Test Container
# Using Node 22 with Playwright for stability
FROM mcr.microsoft.com/playwright:v1.48.0-noble

# Avoid apt prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install bun (need unzip first)
RUN apt-get update && apt-get install -y --no-install-recommends unzip && \
    rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Copy package files first for better caching
COPY package.json bun.lockb* ./

# Install dependencies with bun (cached unless package.json changes)
RUN bun install --frozen-lockfile || bun install

# Install Playwright browsers
RUN bunx playwright install chromium --with-deps

# Copy config files
COPY tsconfig.json playwright.config.ts ./

# Copy test files (changes frequently, so copy last)
COPY tests/ ./tests/

# Create results directories
RUN mkdir -p playwright-report test-results fixtures

# Set environment variables
ENV CI=true
ENV WEB_URL=http://admin:5173
ENV ADMIN_URL=http://admin:5173
ENV FUNCTIONS_URL=http://functions:80

# Default command using bun
CMD ["bunx", "playwright", "test", "--reporter=list"]
