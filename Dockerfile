# Stage 1: Frontend Builder
FROM node:18-alpine AS builder
WORKDIR /web
# Copy package files and install dependencies
COPY web/package.json web/package-lock.json* ./
RUN npm install
# Copy the rest of the frontend source
COPY web/ ./
# Build the production React files
RUN npm run build || true

# Stage 2: Backend Runner
FROM python:3.10-slim
WORKDIR /app

# Install backend requirements
COPY api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend Python code
COPY api/ ./

# Copy the local adv_rag_eval library so main.py can import it
COPY adv_rag_eval/ ./adv_rag_eval/

# Copy built React frontend to the path expected by FastAPI StaticFiles
COPY --from=builder /web/dist /app/dist

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 2: Backend Runner
FROM python:3.10-slim
WORKDIR /app

# --- NEW: Install Build Tools for C++ Compilation ---
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# ----------------------------------------------------

# Install backend requirements
COPY api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend Python code
COPY api/ ./

# Copy the local adv_rag_eval library
COPY adv_rag_eval/ ./adv_rag_eval/

# Copy built React frontend
COPY --from=builder /web/dist /app/dist

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]