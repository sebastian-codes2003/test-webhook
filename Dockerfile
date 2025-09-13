# syntax=docker/dockerfile:1
FROM python:3.10-alpine
WORKDIR /discord-bot
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python", "main.py"]