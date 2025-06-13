from werkzeug.security import generate_password_hash
from config import Config
import pymysql

def create_database():
    conn = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
    finally:
        conn.close()

def get_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def create_tables():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Tabla productos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion VARCHAR(250),
                    precio DECIMAL(10,2) NOT NULL,  # Mejor tipo para dinero
                    stock DECIMAL(10,2) NOT NULL,
                    unidad VARCHAR(10) NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Tabla usuarios con contraseñas hasheadas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,  # Más largo para hashes
                    rol ENUM('admin', 'usuario') NOT NULL DEFAULT 'usuario',
                    activo BOOLEAN DEFAULT TRUE
                )
            """)

            # Insertar datos iniciales
            cursor.execute("SELECT COUNT(*) AS total FROM productos")
            if cursor.fetchone()["total"] == 0:
                productos = [
                    ('Arroz', 'Blanco', 11.90, 10.0, 'kg'),
                    ('Papa amarilla', 'Sin descripción', 3.2, 8.0, 'kg'),
                    ('Papa blanca', 'Sin descripción', 2.8, 8.0, 'kg'),
                    ('Cebolla', 'Blanca', 5.5, 5.0, 'kg'),
                    ('Tomate', 'Italiano', 8.0, 5.0, 'kg'),
                    ('Limón', 'Tahiti', 4.9, 3.0, 'kg'),
                ]
                cursor.executemany(
                    "INSERT INTO productos (nombre, descripcion, precio, stock, unidad) VALUES (%s, %s, %s, %s, %s)",
                    productos
                )

            # Usuario admin con contraseña hasheada
            cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE username = 'admin'")
            if cursor.fetchone()["total"] == 0:
                hashed_pw = generate_password_hash('admin123')  # Contraseña más segura
                cursor.execute(
                    "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)",
                    ('admin', hashed_pw, 'admin')
                )
            
            # Usuario alvaro con contraseña hasheada
            cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE username = 'alvaro'")
            if cursor.fetchone()["total"] == 0:
                hashed_pw = generate_password_hash('SecurePass123')
                cursor.execute(
                    "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)",
                    ('alvaro', hashed_pw, 'usuario')
                )

        conn.commit()