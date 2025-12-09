# CarvyRecortImg AI Orchestrator

Este proyecto es un orquestador de API construido con FastAPI que automatiza el proceso de generación, procesamiento y almacenamiento de imágenes de vehículos.

## Descripción

El objetivo principal es orquestar varias tareas de IA y almacenamiento en la nube a través de una API simple. El flujo de trabajo incluye la generación de imágenes de coches a partir de descripciones de texto, la eliminación del fondo de las imágenes, y el almacenamiento de los resultados en un bucket de Supabase para su uso futuro. También proporciona un endpoint para subir, procesar y almacenar imágenes existentes.

## Características

- **Generación de Imágenes con IA**: Utiliza la API de Gemini de Google para generar imágenes de coches a partir de marca, modelo y año.
- **Eliminación de Fondo de Alta Calidad**: Emplea la librería `rembg` con modelos de precisión (`u2net`) para quitar el fondo de las imágenes.
- **Caché de Imágenes**: Antes de generar una nueva imagen, verifica si ya existe en Supabase para ahorrar recursos.
- **Subida y Procesamiento Personalizado**: Endpoint para subir tus propias imágenes, quitarles el fondo y guardarlas con un nombre personalizado.
- **Seguridad**: Los endpoints están protegidos por una API Key.
- **Contenerizado**: Totalmente contenerizado con Docker para un despliegue fácil y consistente.

## Prerrequisitos

Antes de empezar, asegúrate de tener lo siguiente:

- [Docker](https://www.docker.com/get-started) instalado.
- Una cuenta en [Google AI Studio](https://aistudio.google.com/) para obtener una `GOOGLE_API_KEY`.
- Una cuenta en [Supabase](https://supabase.com/) con un proyecto creado y un bucket de almacenamiento llamado `images`.

## Instalación y Puesta en Marcha

1.  **Clona el repositorio**:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd carvyrecortimg
    ```

2.  **Configura las variables de entorno**:
    Crea un archivo llamado `.env` en la raíz del proyecto y añade las siguientes variables:

    ```env
    # Clave secreta para proteger tus endpoints
    API_KEY_SECRET="TU_CLAVE_SECRETA_PERSONALIZADA"

    # Credenciales de la API de Gemini
    GOOGLE_API_KEY="TU_API_KEY_DE_GOOGLE"

    # Credenciales de tu proyecto de Supabase
    SUPABASE_URL="https://xxxxxxxx.supabase.co"
    SUPABASE_SERVICE_ROLE_KEY="TU_CLAVE_DE_SERVICIO_DE_SUPABASE"
    ```

3.  **Construye y ejecuta el contenedor Docker**:
    ```bash
    # Construye la imagen de Docker
    docker build -t car-bg-api .

    # Ejecuta el contenedor
    docker run -p 8000:8000 -v .:/app car-bg-api
    ```
    La API ahora estará disponible en `http://localhost:8000`.

## Documentación de la API

Puedes acceder a la documentación interactiva de la API (generada por Swagger UI) en `http://localhost:8000/docs`.

### 1. Generar y Procesar una Imagen Nueva

- **Endpoint**: `/generate-and-process`
- **Método**: `POST`
- **Cabecera**: `x-api-key: TU_CLAVE_SECRETA_PERSONALIZADA`
- **Parámetros (Query)**:
    - `marca` (string, requerido): La marca del coche (ej. "honda").
    - `modelo` (string, requerido): El modelo del coche (ej. "civic").
    - `year` (integer, requerido): El año del coche (ej. 2023).
    - `car_color` (string, opcional): El color del coche.
    - `car_type` (string, opcional): El tipo de coche (ej. "sedan").
    - `background_color_name` (string, opcional): El color de fondo deseado.

**Ejemplo de uso con `curl`**:
```bash
curl -X POST "http://localhost:8000/generate-and-process?marca=audi&modelo=r8&year=2023&car_color=red" \
-H "x-api-key: TU_CLAVE_SECRETA_PERSONALIZADA"
```

### 2. Subir y Procesar una Imagen Existente

- **Endpoint**: `/upload-and-process`
- **Método**: `POST`
- **Cabecera**: `x-api-key: TU_CLAVE_SECRETA_PERSONALIZADA`
- **Cuerpo (Form-Data)**:
    - `file`: El archivo de imagen que quieres subir.
    - `file_name`: El nombre con el que quieres guardar la imagen procesada (ej. `mi-imagen.png`).

**Ejemplo de uso con `curl`**:
```bash
curl -X POST "http://localhost:8000/upload-and-process" \
-H "x-api-key: TU_CLAVE_SECRETA_PERSONALIZADA" \
-F "file=@/ruta/a/tu/imagen.jpg" \
-F "file_name=mi-imagen-procesada.png"
```

## Modelos Utilizados

- **Generación de Imagen**: `gemini-2.5-flash-image`
- **Remoción de Fondo**: `u2net`