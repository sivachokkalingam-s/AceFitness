FROM python:3.10-slim

# Avoid unnecessary cache → smaller image
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "Aceestver.py"]