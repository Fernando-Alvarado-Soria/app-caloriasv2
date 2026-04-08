FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Copiar código de la app
COPY app/ app/
COPY ml/ ml/
COPY server/ server/

# Railway asigna un puerto dinámico via $PORT, default 8000
EXPOSE 8000

# Comando de inicio — usa $PORT de Railway o 8000 por defecto
CMD uvicorn server.api:app --host 0.0.0.0 --port ${PORT:-8000}
