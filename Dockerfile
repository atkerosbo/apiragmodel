# Step 1: Choose the base image for Python
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc build-essential
# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements.txt file
COPY requirements.txt .

# Step 4: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code
COPY /src /app

# Step 6: Set environment variables (optional, adjust according to your app)

# Step 7: Expose the port your app will run on (optional, adjust accordingly)
EXPOSE 8000

# Step 8: Define the default command to run the app (adjust according to your app)

# Run the command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]