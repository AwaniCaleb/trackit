FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so this layer is cached unless requirements change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the files the service needs at runtime
COPY main.py ecg_processor.py ./

EXPOSE 8000

# main.py reads PORT from the environment (defaults to 8000)
CMD ["python", "main.py"]
