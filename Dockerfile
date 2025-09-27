# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /discord-bot

# Instalar dependencias primero (capa cacheable)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

EXPOSE 5000

# Arrancar la app (usa Flask run o Python, según tu main.py)
CMD ["python", "main.py"]
