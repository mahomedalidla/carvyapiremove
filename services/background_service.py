# services/background_service.py

import io
from rembg import remove, new_session
from PIL import Image, ImageEnhance
import os

# --- CONFIGURACIÓN DEL MODELO ---
# Se cambia a 'u2net' para mayor precisión. Es más pesado que 'u2netp'.
# Asegúrate de que el entorno (Docker) tenga suficiente RAM (se recomienda >1GB).
MODEL_NAME = os.getenv("MODEL_NAME", "u2net")
print(f"Background Service: Cargando modelo de remoción: {MODEL_NAME}")
session = new_session(MODEL_NAME)


def remove_background_precise(image_bytes: bytes) -> io.BytesIO:
    """
    Remueve el fondo de la imagen usando un modelo de alta precisión
    y parámetros ajustados para conservar los detalles del vehículo.

    Args:
        image_bytes: Los datos binarios (bytes) de la imagen a procesar.

    Returns:
        io.BytesIO: Un buffer de memoria con la imagen PNG transparente.
    """
    
    # 1. Cargar imagen desde los bytes recibidos
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    
    # 2. Remover fondo con parámetros de precisión
    output = remove(
        img,
        session=session,
        alpha_matting=True,
        # Se reduce el tamaño de la erosión para no perder detalles finos del coche.
        alpha_matting_foreground_threshold=270, 
        alpha_matting_background_threshold=20,
        alpha_matting_erode_size=2 
    )
    
    # 3. Refuerzo de nitidez en el canal alfa (Contraste Quirúrgico)
    # Este paso ayuda a que los bordes semitransparentes sean más definidos.
    r, g, b, a = output.split()
    enhancer = ImageEnhance.Contrast(a)
    a = enhancer.enhance(2.0) # Se reduce ligeramente el contraste para un efecto menos duro.
    output = Image.merge("RGBA", (r, g, b, a))
    
    # 4. Guardar resultado en un buffer de memoria PNG
    output_buffer = io.BytesIO()
    output.save(output_buffer, format="PNG", compress_level=1)
    output_buffer.seek(0)
    return output_buffer

# Ejemplo de uso:
if __name__ == '__main__':
    # Esto es solo para pruebas locales
    print(remove_background_precise(b'datos de imagen de prueba'))