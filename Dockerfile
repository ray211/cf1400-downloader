# Use an official Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy your app code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run the microservice
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
