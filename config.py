import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables de entorno desde .env

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'bodega')
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu_clave_secreta_compleja')