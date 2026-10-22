FROM python:3.11-slim

# Setează directorul de lucru în container
WORKDIR /app

# Copiază lista de cerințe și instalează pachetele
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiază restul codului în container
COPY . .

# Pornește botul
CMD ["python", "bot.py"]
