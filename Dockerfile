# syntax=docker/dockerfile:1
FROM python:3.11-slim

# ---- System setup ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    libc6 curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Rust-based pip/pip-tools replacement)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

# ---- Dependency management ----
# Copy only requirements folder first for better build caching
COPY requirements/ ./requirements/

# Compile and install dependencies (fresh from .in each build)
RUN uv pip compile requirements/requirements.in -o requirements.txt && \
    uv pip install --system -r requirements.txt

# ---- Application code ----
COPY . .

# Copy your custom Stockfish binary and make it executable
COPY ./stockfish_bin/patched_stockfish /app/stockfish_bin/patched_stockfish
RUN chmod +x /app/stockfish_bin/patched_stockfish

# ---- Runtime configuration ----
EXPOSE 8080

# Start FastAPI app on Cloud Run
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]
