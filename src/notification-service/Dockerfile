# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /src

# Copy requirements.txt
COPY requirements.txt /src

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY /app /src/app

# Define environment variables
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["python", "-m", "app.new_consumer"]
