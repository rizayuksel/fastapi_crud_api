# Python 3.11 base image
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıklarını kur (PostgreSQL için gerekli)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Requirements'ı kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı kopyala
COPY ./app ./app

# Port expose et
EXPOSE 8000

# Başlangıç komutu
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
