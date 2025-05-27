# Use official Python 3.10 slim image as the base image
FROM python:3.10-slim

# Set the working directory for the executor container
WORKDIR /executor

# Copy executor.py and requirements-executor.txt into the container
COPY executor.py requirements-executor.txt ./

# Install Python dependencies from requirements-executor.txt
RUN pip install --no-cache-dir -r requirements-executor.txt

# Expose the port the executor will run on
EXPOSE 9000

# Command to start the FastAPI executor app using uvicorn
CMD ["uvicorn", "executor:app", "--host", "0.0.0.0", "--port", "9000"]
