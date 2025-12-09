from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv() 

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") 
BUCKET = "images"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🛑 1. check_if_exists: Función renombrada y corregida
def check_if_exists(filename: str) -> str | None:
    try:
        files = supabase.storage.from_(BUCKET).list()
        if any(f["name"] == filename for f in files):
            public_url = supabase.storage.from_(BUCKET).get_public_url(filename)
            return public_url
        return None
    except Exception:
        return None

# 🛑 2. upload_image: Modificada para aceptar bytes directamente
def upload_image(filename: str, file_bytes: bytes) -> str:
    supabase.storage.from_(BUCKET).upload(
        path=filename,
        file=file_bytes, # <-- Subimos los bytes directamente
        file_options={"content-type": "image/png"}
    )
    return supabase.storage.from_(BUCKET).get_public_url(filename)