FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# gunicorn pour un serveur de prod léger (au lieu de app.run en dev)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
