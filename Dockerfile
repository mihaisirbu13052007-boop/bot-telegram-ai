FROM python:3.11-slim

WORKDIR /app

# Instalăm pachetele direct, fără să mai căutăm requirements.txt
RUN pip install --no-cache-dir python-telegram-bot groq

# Copiază scriptul botului în container
COPY bot.py .

# Pornește botul
CMD ["python", "bot.py"]
