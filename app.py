from flask import Flask
from routes import init_routes
from init_db import create_database, create_tables

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Inicializar la base de datos y las tablas
create_database()
create_tables()

# Inicializar las rutas
init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
