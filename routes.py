from flask import render_template, request, redirect, session, url_for, flash
import pymysql
from functools import wraps
from models import get_productos, conectar_db, eliminar_producto
from werkzeug.security import check_password_hash


def init_routes(app):
    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrap

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            usuario = request.form["usuario"]
            password = request.form["password"]
            db = conectar_db()
            cursor = db.cursor()
            
            # Primero buscar solo por nombre de usuario
            cursor.execute("SELECT id, password, rol FROM usuarios WHERE username = %s", (usuario,))
            resultado = cursor.fetchone()
            db.close()

            if resultado and check_password_hash(resultado["password"], password):
                session["user_id"] = resultado["id"]
                session["username"] = usuario
                session["rol"] = resultado["rol"]
                return redirect(url_for("index"))
            else:
                flash("Usuario o contraseña incorrectos")

        return render_template("login.html")
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        conn = conectar_db()
        cursor = conn.cursor()

        # KPIs
        cursor.execute("""
            SELECT SUM(precio * cantidad) AS total_ventas 
            FROM movimientos 
            WHERE tipo = 'venta'
        """)
        total_ventas = cursor.fetchone()["total_ventas"] or 0

        cursor.execute("SELECT COUNT(*) AS stock_bajo FROM productos WHERE stock <= 5")
        stock_bajo = cursor.fetchone()['stock_bajo']

        cursor.execute("SELECT COUNT(*) AS total_productos FROM productos")
        total_productos = cursor.fetchone()['total_productos']

        # Datos para gráficos
        cursor.execute("""
            SELECT DATE(fecha) AS fecha, SUM(precio * cantidad) AS total
            FROM movimientos
            WHERE tipo = 'venta'
            GROUP BY fecha
            ORDER BY fecha DESC
            LIMIT 7
        """)
        ventas_diarias = cursor.fetchall()

        cursor.execute("""
            SELECT categoria, SUM(stock) AS total_stock
            FROM productos
            GROUP BY categoria
        """)
        stock_por_categoria = cursor.fetchall()

        # Últimos movimientos (no solo ventas)
        cursor.execute("""
            SELECT m.fecha, p.nombre, m.cantidad, m.tipo
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            ORDER BY m.fecha DESC
            LIMIT 10
        """)
        movimientos = cursor.fetchall()

        conn.close()

        return render_template(
            'dashboard.html',
            total_ventas=total_ventas,
            stock_bajo=stock_bajo,
            total_productos=total_productos,
            ventas_diarias=ventas_diarias[::-1],  # De más antiguo a reciente
            stock_por_categoria=stock_por_categoria,
            movimientos=movimientos
        )


    @app.route('/')
    @login_required
    def index():
        productos = get_productos()
        return render_template('index.html', productos=productos, active_page='inventario')

    @app.route('/vender/<int:producto_id>', methods=['GET'])
    @login_required
    def form_vender(producto_id):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, stock, unidad FROM productos WHERE id = %s", (producto_id,))
        producto = cursor.fetchone()
        conn.close()

        return render_template('vender.html', producto=producto, active_page='inventario')

    @app.route('/agregar', methods=['GET', 'POST'])
    @login_required
    def agregar_producto():
        if 'rol' not in session or session['rol'] != 'admin':
            return redirect(url_for('index'))

        if request.method == 'POST':
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = request.form['precio']
            stock = request.form['stock']
            unidad = request.form['unidad']

            conn = conectar_db()
            cursor = conn.cursor()

            # Insertar el producto
            cursor.execute(
                "INSERT INTO productos (nombre, descripcion, precio, stock, unidad) VALUES (%s, %s, %s, %s, %s)",
                (nombre, descripcion, precio, stock, unidad)
            )

            # Obtener el id del nuevo producto
            producto_id = cursor.lastrowid

            # Registrar el movimiento
            cursor.execute(
                "INSERT INTO movimientos (producto_id, cantidad, precio, tipo) VALUES (%s, %s, %s, 'agregado')",
                (producto_id, stock, precio)
            )

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('index'))

        return render_template('agregar.html', active_page='agregar')

    @app.route('/procesar_accion/<int:producto_id>', methods=['POST'])
    @login_required
    def procesar_accion_producto(producto_id):
        cantidad = float(request.form['cantidad'])
        accion = request.form['accion']
        conn = conectar_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            "SELECT stock, precio, nombre, unidad FROM productos WHERE id = %s",
            (producto_id,)
        )
        row = cursor.fetchone()

        if row is None:
            flash("Producto no encontrado", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('index'))

        stock_actual = row['stock']
        precio = row['precio']
        nombre = row['nombre']
        unidad = row['unidad']

        if accion == 'reabastecer':
            cursor.execute(
                "UPDATE productos SET stock = stock + %s WHERE id = %s",
                (cantidad, producto_id)
            )
            cursor.execute(
                "INSERT INTO movimientos (producto_id, cantidad, precio, tipo) VALUES (%s, %s, %s, 'reabastecimiento')",
                (producto_id, cantidad, precio)
            )
        elif accion == 'vender':
            if stock_actual < cantidad:
                flash("Stock insuficiente", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for('index'))

            cursor.execute(
                "UPDATE productos SET stock = stock - %s WHERE id = %s",
                (cantidad, producto_id)
            )
            cursor.execute(
                "INSERT INTO movimientos (producto_id, cantidad, precio, tipo) VALUES (%s, %s, %s, 'venta')",
                (producto_id, cantidad, precio)
            )

        # Consulta el stock actualizado
        cursor.execute(
            "SELECT stock FROM productos WHERE id = %s",
            (producto_id,)
        )
        nuevo_stock = cursor.fetchone()['stock']

        # Verifica si el stock es bajo
        if nuevo_stock <= 5:
            mensaje = f"⚠ ALERTA: El stock de {nombre} es bajo ({nuevo_stock} {unidad})"
            enviar_alerta_whatsapp(NUMERO_ADMIN, mensaje, API_KEY)

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))


    @app.route('/editar/<int:id>', methods=['GET', 'POST'])
    def editar(id):
        if 'rol' not in session or session['rol'] != 'admin':
            return redirect(url_for('index'))
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
        producto = cursor.fetchone()

        if request.method == 'POST':
            nuevo_nombre = request.form['nombre']
            nuevo_descripcion = request.form['descripcion']
            nuevo_precio = request.form['precio']
            nuevo_stock = request.form['stock']
            nueva_unidad = request.form['unidad']
            
            cursor.execute(
                'UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, stock=%s, unidad=%s WHERE id=%s',
                (nuevo_nombre, nuevo_descripcion, nuevo_precio, nuevo_stock, nueva_unidad, id)
            )
            delta_stock = float(nuevo_stock) - float(producto['stock'])
            if delta_stock != 0:
                cursor.execute(
                    "INSERT INTO movimientos (producto_id, cantidad, precio, tipo) VALUES (%s, %s, NULL, 'ajuste')",
                    (id, delta_stock)
    )
            conn.commit()
            cursor.execute("SELECT nombre, stock, unidad FROM productos WHERE id = %s", (id,))
            producto = cursor.fetchone()
            if producto['stock'] <= 5:
                mensaje = f"⚠ ALERTA: El stock de {producto['nombre']} es bajo ({producto['stock']} {producto['unidad']})"
                enviar_alerta_whatsapp(NUMERO_ADMIN, mensaje, API_KEY)

            conn.close()
            return redirect(url_for('index'))
        
        conn.close()
        return render_template('editar.html', producto=producto, active_page='inventario')

    @app.route("/eliminar/<int:id>", methods=["POST"])
    def eliminar(id):
        if 'rol' not in session or session['rol'] != 'admin':
            return redirect(url_for('index'))
        eliminar_producto(id)
        return redirect(url_for("index"))
    
    from utils.whatsapp_alert import enviar_alerta_whatsapp
    # Configura tu número y api_key
    NUMERO_ADMIN = "+51989014501"  # Cambia por tu número
    API_KEY = "7178632"        # La que te dio CallMeBot

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
