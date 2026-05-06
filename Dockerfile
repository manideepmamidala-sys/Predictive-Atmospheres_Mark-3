# Use the official lightweight Python image.
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the console
ENV PYTHONUNBUFFERED True

# Set the working directory
WORKDIR /app

# Copy requirement or pyproject files
COPY pyproject.toml .

# Install dependencies early so that they can be cached
RUN pip install --no-cache-dir .

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
