# Etapa 1: Builder
FROM public.ecr.aws/docker/library/python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 2: Runtime
FROM public.ecr.aws/docker/library/python:3.11-slim
WORKDIR /app

# Copiar dependencias desde la etapa builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copiar ejecutables (gunicorn y otros scripts)
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código fuente del proyecto
COPY app/ ./app/
COPY run.py .

# Variables de entorno
ENV FLASK_ENV=production
ENV PORT=5000

# Exponer el puerto de la aplicación
EXPOSE 5000

# Comando de inicio usando Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]
