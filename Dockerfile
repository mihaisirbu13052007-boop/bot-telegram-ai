FROM python:3.11-slim

WORKDIR /app

# Instalăm pachetele incluzând extensia de webhooks pentru Telegram
RUN pip install --no-cache-dir "python-telegram-bot[webhooks]" groq

# Copiază scriptul botului în container
COPY bot.py .

# Pornește botul
CMD ["python", "bot.py"]
