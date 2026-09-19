# Use Python 3.11 slim image for efficiency
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8081 for incoming connections
EXPOSE 8081

# Run the SSE server
CMD ["python", "terminal_server_sse.py"]