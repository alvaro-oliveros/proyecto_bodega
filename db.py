# db.py
import pymysql

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='bodega',
        cursorclass=pymysql.cursors.DictCursor  # Esto devuelve los resultados como diccionarios
    )
