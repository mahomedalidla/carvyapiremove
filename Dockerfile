# Usamos una imagen ligera de Python
FROM python:3.11-slim

# Instalamos dependencias actualizadas para procesamiento de imágenes
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos e instalamos requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🛑 ¡CORRECCIÓN AQUÍ! 🛑
# Copiamos TODO el contenido del directorio local (main.py, services/, utils/)
COPY . .  

# Exponemos el puerto de FastAPI
EXPOSE 8000

# Comando para arrancar con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]