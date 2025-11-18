# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/requirements.txt .
COPY backend/server.py .
COPY backend/.env .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8001

# Start command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
