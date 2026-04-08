FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar PyTorch CPU-only primero (mucho más liviano)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copiar requirements e instalar el resto
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Copiar código de la app
COPY app/ app/
COPY ml/ ml/
COPY server/ server/

# Puerto por defecto
ENV PORT=8000
EXPOSE 8000

# Comando de inicio
CMD uvicorn server.api:app --host 0.0.0.0 --port ${PORT}
