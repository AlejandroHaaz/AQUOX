import json
import os
from dotenv import load_dotenv
from datetime import timedelta

# Cargar las variables desde el archivo .env
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
   
    # Procesar credenciales de Google al inicio
    RAW_GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    GOOGLE_APPLICATION_CREDENTIALS_JSON = json.loads(RAW_GOOGLE_CREDENTIALS) if RAW_GOOGLE_CREDENTIALS else None

    # Corregir saltos de línea en private_key si está definido
    if GOOGLE_APPLICATION_CREDENTIALS_JSON:
        GOOGLE_APPLICATION_CREDENTIALS_JSON['private_key'] = GOOGLE_APPLICATION_CREDENTIALS_JSON['private_key'].replace("\\n", "\n")
