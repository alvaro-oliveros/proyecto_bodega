# models.py
import pymysql

def conectar_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='bodega',
        cursorclass=pymysql.cursors.DictCursor  # opcional, si quieres usar nombres de columnas
    ) 

def get_productos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, descripcion, precio, stock, unidad FROM productos")
    columnas = [col[0] for col in cursor.description]
    productos = cursor.fetchall()
    for p in productos:
        try:
            p['stock'] = float(p['stock'])
        except (ValueError, TypeError):
            p['stock'] = 0  # o algún valor predeterminado en caso de error
    conn.close()
    return productos


def actualizar_producto(id, nombre, descripcion, precio, stock, unidad):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, stock=%s, unidad=%s WHERE id=%s",
        (nombre, descripcion, precio, stock, unidad, id)
    )
    conn.commit()
    conn.close()

def eliminar_producto(id):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conn.commit()
    conn.close()

