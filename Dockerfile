# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# --- THIS IS THE FIX ---
# Install the system-level PortAudio library needed by the sounddevice package
RUN apt-get update && apt-get install -y libportaudio2 portaudio19-dev

# Set the working directory in the container
WORKDIR /app

# Copy the file that lists our requirements
COPY requirements.txt .

# Install the Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define the command to run your app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]