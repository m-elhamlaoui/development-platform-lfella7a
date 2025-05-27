FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY cyanonet_api.py .

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "cyanonet_api:app", "--host", "0.0.0.0", "--port", "8000"] 