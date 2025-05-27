# Use official Python 3.10 slim image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy server.py and requirements.txt into the container
COPY server.py requirements.txt ./

COPY index.html ./
# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the EXECUTOR_URL environment variable so the API container can reach the executor container via DNS
ENV EXECUTOR_URL=http://executor:9000/execute

# Expose the port the API will run on
EXPOSE 8000

# Command to start the FastAPI app using uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
