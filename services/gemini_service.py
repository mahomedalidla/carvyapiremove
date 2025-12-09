import os
import logging
import io
import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_KEY:
    raise ValueError("GOOGLE_API_KEY no configurada en el entorno.")

try:
    genai.configure(api_key=GEMINI_KEY)
except Exception as e:
    logger.error(f"FALLO en la configuración de Gemini: {e}")
    raise

# --- FUNCIÓN DE SERVICIO CORREGIDA ---
def generate_image(make: str, car_model: str, year: int, car_color: str | None = None, car_type: str | None = None, background_color_name: str | None = None) -> bytes:
    logger.info(f"🔧 Generando imagen para: {year} {make} {car_model} (Color: {car_color}, Tipo: {car_type}, Fondo: {background_color_name})")

    # Construir el prompt con los nuevos parámetros
    prompt = f"Generate a photorealistic image of a {make} {car_model} {year}"
    if car_color:
        prompt += f", color {car_color}"
    if car_type:
        prompt += f", type {car_type}"
    prompt += ".\n\nCRITICAL STUDIO SETUP:\n"

    if background_color_name:
        prompt += f"1. BACKGROUND: {background_color_name}\n"
        prompt += f"2. FLOOR: {background_color_name}\n"
        prompt += f"3. SHADOWS: NO CAST SHADOWS. The car must appear to be FLOATING in a {background_color_name} void. Do not render shadow contact on the floor.\n"
    else:
        prompt += "1. BACKGROUND: clean, solid light-gray\n"
        prompt += "2. FLOOR: clean, solid light-gray\n"
        prompt += "3. SHADOWS: NO CAST SHADOWS. The car must appear to be FLOATING in a clean, solid light-gray void. Do not render shadow contact on the floor.\n"

    prompt += (
        "4. LIGHTING: Soft studio lighting. Evenly lit. High contrast.\n"
        "5. WINDOWS: PURE SOLID BLACK OPAQUE (Limo Tint). NO TRANSPARENCY inside the car. NO REFLECTIONS on windows.\n"
        "6. REFLECTIONS: Minimize floor reflections.\n"
        "7. VIEW: 3/4 Front View.\n"
        "8. QUALITY: 4k, Sharp edges.\n"
        "9. Asegúrate de que los rines son los originales que trae el auto de agencia.\n"
        "10. El auto debe de abarcar el 90% del ancho de la imagen.\n"
        "11. No debe de reflejarse el auto en el suelo.\n\n"
        "GOAL: Ensure high contrast between subject and background."
    )
    
    logger.info(f"Prompt para Gemini: {prompt}")

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-image')
        logger.info("Generando contenido con Gemini...")
        
        # Para la generación de imágenes, es posible que se necesite una configuración específica.
        # Basado en la documentación, la respuesta puede contener los datos directamente.
        response = model.generate_content(prompt)
        
        
        logger.info("Respuesta de Gemini recibida. Procesando...")

        # Estructura de respuesta esperada para imágenes
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            all_text_parts = []
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                    image_bytes = part.inline_data.data
                    logger.info(f"✅ Imagen generada por Gemini ({len(image_bytes)} bytes).")
                    return image_bytes
                elif hasattr(part, 'text'):
                    all_text_parts.append(part.text)
            
            # Si el bucle termina y no se encontró una imagen, se lanza una excepción.
            full_text_response = "".join(all_text_parts)
            logger.error(f"No se encontró ninguna parte con datos de imagen. Contenido de texto combinado: '{full_text_response}'")
            raise Exception(f"Gemini devolvió texto en lugar de una imagen: '{full_text_response}'")
        else:
            # Si la respuesta es texto (ej. un error o mensaje), lo registramos.
            text_response = response.text if hasattr(response, 'text') else 'Respuesta vacía o con estructura inesperada.'
            logger.error(f"Respuesta inesperada de Gemini (no es imagen): {text_response}")
            raise Exception(f"Gemini devolvió un mensaje en lugar de una imagen: {text_response}")

    except Exception as e:
        logger.error(f"Error en la llamada a la API de Gemini: {e}", exc_info=True)
        raise Exception(f"Fallo en la comunicación con la API de Gemini: {e}") from e
