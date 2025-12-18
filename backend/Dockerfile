# Imagen base con Python 3.12 slim
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /proyecto

# Copiar solo requirements para cachear instalación deps
COPY requerimientos.txt .

# Instalar dependencias
RUN pip install -r requerimientos.txt

RUN mkdir -p /proyecto/app
# Copiar el resto del código
COPY ./app ./app

# Comando para desarrollo con reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
