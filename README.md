# Asistente de Stock para Bodegas 🏪

Sistema web simple hecho en Flask + MySQL para gestionar inventario de productos en bodegas o cocinas.

## Funcionalidades actuales
- Visualización del stock con colores (verde, amarillo, rojo)
- Agregar, editar, eliminar productos
- Control por roles (admin, vendedor)
- Alerta visual por stock bajo

## Requisitos
- Python 3.10+
- MySQL
- Flask
- PyMySQL

## Paso Previo
Tener el xampp con mysql
cd C:\xampp\mysql\bin
mysql -u root -p

## Instalación
```bash
git clone https://github.com/alvaro-oliveros/proyecto_bodega.git
cd stock-bodega
python3 -m venv env # py -m venv env (Windows)
source env/bin/activate  # env\Scripts\activate (Windows)
pip install -r requirements.txt
python app.py # py app.py