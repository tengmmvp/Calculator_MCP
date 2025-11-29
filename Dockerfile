# Multi-stage build for Calculator MCP Server
FROM python:3.11-slim as builder

# Set build arguments
ARG VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF

# Set labels
LABEL maintainer="Calculator MCP Team <admin@tengmmvp.cn>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="calculator-mcp-server" \
      org.label-schema.description="A complete Model Context Protocol (MCP) compliant mathematical calculation server" \
      org.label-schema.url="https://github.com/tengmmvp/Calculator_MCP" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/tengmmvp/Calculator_MCP.git" \
      org.label-schema.vendor="Calculator MCP Team" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user
RUN addgroup --system app && adduser --system --group app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies and build tools
RUN pip install --upgrade pip && \
    pip install fastmcp>=2.13.0 pydantic>=2.11.7 hatchling

# Copy application code
COPY calculator_mcp/ ./calculator_mcp/

# Install the package
RUN pip install -e .

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/app/.local/bin:$PATH"

# Create app user
RUN addgroup --system app && adduser --system --group app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app /app

# Set work directory
WORKDIR /app

# Change ownership to app user
RUN chown -R app:app /app

# Switch to app user
USER app

# Expose port (if server runs on HTTP)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["calculator-mcp-server"]