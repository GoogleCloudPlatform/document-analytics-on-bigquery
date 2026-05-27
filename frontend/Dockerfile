# Use official slim Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Set working directory
WORKDIR /app

# Install system dependencies (poppler-utils is required by pdf2image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py ./
COPY style.css ./
COPY app_config.yaml ./


# Expose port (Cloud Run sets this env variable automatically)
EXPOSE 8080

# Start Streamlit, binding to 0.0.0.0 and using the dynamic PORT env var
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]
