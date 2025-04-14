FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy client code
COPY self_awareness_client.py .
COPY example_ai_agent.py .

# Run the example AI agent
CMD ["python", "example_ai_agent.py"]
