FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (needed for spaCy compilation)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
# Railway builds from root, so use backend/ prefix
COPY backend/requirements.txt .

# Install Python dependencies in two stages for faster builds
# Stage 1: Fast packages (no compilation needed)
# Stage 2: spaCy (may need compilation, but prefer wheels)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefer-binary \
        fastapi==0.116.0 \
        uvicorn[standard]==0.34.0 \
        python-multipart==0.0.20 \
        pydantic==2.10.3 \
        supabase==2.9.1 \
        httpx \
        python-dotenv==1.0.1 \
        nltk==3.9.1 \
        wordfreq==3.0.1 && \
    pip install --no-cache-dir --prefer-binary spacy==3.7.2

# Download spaCy model and NLTK data in one layer
RUN python -m spacy download en_core_web_sm && \
    python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# Copy application code (Railway builds from root)
COPY backend/ .

# Expose port
EXPOSE 8080

# Run the application
ENV PORT=8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]



