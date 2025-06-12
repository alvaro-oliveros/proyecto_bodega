# init_db.py
import pymysql

def create_database():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS bodega")
    conn.commit()
    cursor.close()
    conn.close()

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="bodega",
        cursorclass=pymysql.cursors.DictCursor  # para usar diccionarios
    )

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Crear tabla productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100),
            descripcion VARCHAR(250),
            precio FLOAT,
            stock FLOAT,
            unidad VARCHAR(10)
        )
    """)

    # Insertar productos si está vacía
    cursor.execute("SELECT COUNT(*) AS total FROM productos")
    if cursor.fetchone()["total"] == 0:
        productos = [
            ('Arroz', 'Blanco', 11.90, 10.0, 'kg'),
            ('Papa amarilla', '', 3.2, 8.0, 'kg'),
            ('Papa blanca', '', 2.8, 8.0, 'kg'),
            ('Cebolla', 'Blanca', 5.5, 5.0, 'kg'),
            ('Tomate', 'Italiano', 8.0, 5.0, 'kg'),
            ('Limón', 'Tahiti', 4.9, 3.0, 'kg'),
        ]
        cursor.executemany("INSERT INTO productos (nombre, descripcion, precio, stock, unidad) VALUES (%s, %s, %s, %s, %s)", productos)

    # Crear tabla usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(100) NOT NULL,
            rol VARCHAR(20) NOT NULL
        )
    """)

    # Insertar usuario admin si no existe
    cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE username = 'admin'")
    if cursor.fetchone()["total"] == 0:
        cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES ('admin', 'admin', 'admin')")

    # Insertar usuario alvaro si no existe
    cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE username = 'alvaro'")
    if cursor.fetchone()["total"] == 0:
        cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES ('alvaro', '123456', 'usuario')")

    conn.commit()
    cursor.close()
    conn.close()
