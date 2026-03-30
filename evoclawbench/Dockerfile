# EvoClawBench Runtime Docker Image
# Build with: docker build -t evoclawbench/runtime .
# Or: docker build -t evoclawbench/runtime --build-arg NANOBOT_VERSION=0.1.0 .

FROM python:3.11-slim

LABEL maintainer="evoclawbench"
LABEL description="Runtime environment for EvoClawBench skill evolution benchmarking"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install nanobot (latest from source)
RUN uv pip install --system nanobot

# Install openclaw (if available)
# Note: openclaw installation may require additional setup
RUN uv pip install --system openclaw || echo "openclaw installation skipped (may require additional setup)"

# Create working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
