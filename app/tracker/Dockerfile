FROM nginx:alpine

# Install Python and pip, then create and activate virtual environment
RUN apk add --no-cache python3 py3-pip \
    && python3 -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache-dir -r /app/tracker/requirements.txt

# Set working directory
WORKDIR /app/tracker

# Copy only the necessary files into the container
COPY ./app/tracker/ /app/tracker/

# Install the Python dependencies in the virtual environment
RUN /app/venv/bin/pip install --no-cache-dir -r /app/tracker/requirements.txt

# Check the contents of the directory
RUN ls -l /app/tracker

# Start Nginx and your Python app
CMD ["sh", "-c", "nginx && /app/venv/bin/python3 ./backend/app.py"]
