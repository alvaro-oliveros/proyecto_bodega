from flask import render_template, request, redirect, session, url_for, flash
from functools import wraps
from models import get_productos, conectar_db, eliminar_producto

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
            cursor.execute("SELECT id, rol FROM usuarios WHERE username = %s AND password = %s", (usuario, password))
            resultado = cursor.fetchone()
            db.close()

            if resultado:
                session["user_id"] = resultado["id"]
                session["username"] = usuario
                session["rol"] = resultado["rol"]
                return redirect(url_for("index"))
            else:
                flash("Usuario o contraseña incorrectos")

        return render_template("login.html")

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

    @app.route('/vender/<int:producto_id>', methods=['POST'])
    @login_required
    def procesar_venta(producto_id):
        cantidad = float(request.form['cantidad'])

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM productos WHERE id = %s", (producto_id,))
        stock_actual = cursor.fetchone()["stock"]

        if cantidad <= 0:
            flash("Cantidad inválida")
        elif cantidad > stock_actual:
            flash("No hay suficiente stock para vender esa cantidad.")
        else:
            cursor.execute("UPDATE productos SET stock = stock - %s WHERE id = %s", (cantidad, producto_id))
            conn.commit()
            flash(f"Se vendieron {cantidad} unidades.")

        conn.close()
        return redirect(url_for('index'))
    
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
            cursor.execute(
                "INSERT INTO productos (nombre, descripcion, precio, stock, unidad) VALUES (%s, %s, %s, %s, %s)",
                (nombre, descripcion, precio, stock, unidad)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))

        return render_template('agregar.html', active_page='agregar')
    
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
            conn.commit()
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


    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
