# main.py

import logging
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import io

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar Servicios
from services.background_service import remove_background_precise
from services.supabase_service import check_if_exists, upload_image 
from services.gemini_service import generate_image
from utils.helpers import format_file_name

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="CarvyRecortImg AI Orchestrator")

API_KEY_SECRET = os.getenv("API_KEY_SECRET", "ClavePorDefectoNoSegura") 

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Acceso denegado: API Key inválida")
    return x_api_key

# --- ENDPOINT DE UPLOAD Y RECORTE ---
@app.post("/upload-and-process")
async def upload_and_process_image(
    file: UploadFile = File(...),
    file_name: str = Form(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Recibe una imagen, le quita el fondo, y la sube a Supabase con un nombre específico.
    Verifica si ya existe un archivo con ese nombre antes de procesar.
    """
    logger.info(f"Solicitud de carga para el archivo: '{file_name}'")

    # 1. Verificar si el archivo ya existe en Supabase
    logger.info(f"Verificando si '{file_name}' ya existe en Supabase...")
    existing_url = check_if_exists(file_name)
    if existing_url:
        logger.warning(f"El archivo '{file_name}' ya existe. URL: {existing_url}")
        return JSONResponse(
            status_code=409,  # 409 Conflict
            content={"status": "conflict", "message": "Un archivo con este nombre ya existe.", "url": existing_url}
        )

    # 2. Leer los bytes de la imagen subida
    try:
        image_bytes = await file.read()
    except Exception as e:
        logger.error(f"Error al leer el archivo subido: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="No se pudo leer el archivo de imagen.")

    # 3. Remover el fondo de la imagen
    logger.info(f"Procesando remoción de fondo para '{file_name}'...")
    try:
        png_buffer = remove_background_precise(image_bytes)
        processed_image_bytes = png_buffer.getvalue()
        logger.info(f"Remoción de fondo completada para '{file_name}'.")
    except Exception as e:
        logger.error(f"Fallo en la remoción de fondo para '{file_name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fallo en la remoción de fondo: {e}")

    # 4. Almacenar la imagen procesada en Supabase
    logger.info(f"Almacenando '{file_name}' en Supabase...")
    try:
        final_url = upload_image(file_name, processed_image_bytes)
    except Exception as e:
        logger.error(f"Fallo al subir a Supabase para '{file_name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fallo al subir a Supabase: {e}")

    # 5. Respuesta final
    logger.info(f"Proceso de carga completado para '{file_name}'. URL final: {final_url}")
    return JSONResponse(
        status_code=201, 
        content={"status": "created", "file_name": file_name, "url": final_url}
    )


# --- ENDPOINT DE ORQUESTACIÓN PRINCIPAL ---

@app.post("/generate-and-process")
async def generate_and_process_car(
    marca: str, 
    modelo: str, 
    year: int,
    car_color: str | None = None,
    car_type: str | None = None,
    background_color_name: str | None = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Orquesta la creación de imágenes, revisando caché en Supabase, 
    generando con Gemini, removiendo el fondo y almacenando el resultado.
    """
    
    # 1. Formatear Nombre y Prompt
    file_name = format_file_name(marca, modelo, year)
    logger.info(f"[{file_name}] 1. Nombre de archivo generado.")

    # 2. ⚡️ VERIFICAR CACHÉ EN SUPABASE
    logger.info(f"[{file_name}] 2. Buscando en caché de Supabase...")
    existing_url = check_if_exists(file_name)
    
    if existing_url:
        logger.info(f"[{file_name}] ✅ Imagen encontrada en caché. URL: {existing_url}")
        return JSONResponse(
            status_code=200, 
            content={"status": "cached", "url": existing_url}
        )
    
    # 3. 🎨 GENERAR IMAGEN CON GEMINI
    logger.info(f"[{file_name}] ❌ No encontrada. 3. Generando imagen con Gemini...")
    try:
        gemini_output = generate_image(marca, modelo, year, car_color, car_type, background_color_name)
    except Exception as e:
        logger.error(f"Fallo en la generación de Gemini: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fallo en la generación de Gemini: {e}")

    
    # 4. ✂️ REMOVER FONDO
    logger.info(f"[{file_name}] 4. Procesando remoción de fondo con Rembg...")
    try:
        png_buffer = remove_background_precise(gemini_output)
        
        processed_image_bytes = png_buffer.getvalue()
        logger.info(f"[{file_name}] ✅ Remoción de fondo completada.")
    except Exception as e:
        logger.error(f"Fallo en la remoción de fondo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fallo en la remoción de fondo: {e}")

    
    # 5. 💾 ALMACENAR EN SUPABASE
    logger.info(f"[{file_name}] 5. Almacenando imagen PNG en Supabase...")
    try:
        final_url = upload_image(file_name, processed_image_bytes)
    except Exception as e:
        logger.error(f"Fallo al subir a Supabase: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fallo al subir a Supabase: {e}")


    # 6. RESPUESTA FINAL
    logger.info(f"[{file_name}] 🎉 Proceso completado con éxito. URL final: {final_url}")
    return JSONResponse(
        status_code=201, 
        content={"status": "created", "url": final_url}
    )