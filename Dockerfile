FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Verifica a cada 30s se o batimento foi gravado nos últimos 60s.
# Se não foi, container é marcado como "unhealthy" (visível em `docker ps`).
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os,sys,time; sys.exit(0 if time.time()-os.path.getmtime('/tmp/heartbeat.txt') < 60 else 1)"

CMD ["python", "main.py"]