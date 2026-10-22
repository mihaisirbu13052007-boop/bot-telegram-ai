FROM python:3.11-slim

WORKDIR /app

# Instalăm direct pachetele necesare, fără a mai depinde de requirements.txt
RUN pip install --no-cache-dir python-telegram-bot google-generativeai

COPY . .

CMD ["python", "bot.py"]
