# Multi-stage build for smaller final image
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-ai.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt -r requirements-ai.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts in /root/.local are callable
ENV PATH=/root/.local/bin:$PATH

# Install Playwright browsers
RUN playwright install chromium firefox webkit

# Create non-root user
RUN useradd -m -u 1000 testuser && \
    chown -R testuser:testuser /app

# Switch to non-root user
USER testuser

# Environment variables (will be overridden at runtime)
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/home/testuser/.cache/ms-playwright

# Install browsers as testuser
RUN playwright install chromium firefox webkit

# Expose port for API server
EXPOSE 8000

# Default command - can be overridden
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]