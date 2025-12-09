# utils/helpers.py

def format_file_name(marca: str, modelo: str, year: int) -> str:
    """
    Formatea los parámetros en el nombre de archivo requerido: marca_modelo_year.png
    """
    # Limpieza básica para asegurar que sea compatible con URL/Storage
    clean_marca = marca.strip().lower().replace(" ", "-")
    clean_modelo = modelo.strip().lower().replace(" ", "-")
    
    return f"{clean_marca}_{clean_modelo}_{year}.png"