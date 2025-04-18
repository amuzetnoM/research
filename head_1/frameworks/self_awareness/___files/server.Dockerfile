FROM python:3.13-slim-bookworm

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Expose the HTTP port
EXPOSE 8765

# Run the server
CMD ["python", "server.py"]
