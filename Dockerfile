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

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "server.api:app", "--host", "0.0.0.0", "--port", "8000"]
