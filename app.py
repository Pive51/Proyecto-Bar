# app.py
from flask import Flask, render_template, redirect, url_for, session
from controllers.auth_controller import auth_blueprint
from controllers.usuarios_controller import usuarios_blueprint
from database.conexion import obtener_conexion  # Importamos la conexión

# app.py
from controllers.auth_controller import auth_blueprint
from controllers.usuarios_controller import usuarios_blueprint
from controllers.ventas_controller import ventas_blueprint # 1. Importar el nuevo módulo
from controllers.productos_controller import productos_blueprint

app = Flask(__name__)
app.secret_key = 'llave_secreta_bar_pos_ecuador_2026'

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(usuarios_blueprint)
app.register_blueprint(ventas_blueprint)
app.register_blueprint(productos_blueprint)
        
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # --- CONSULTA DE PRODUCTOS EN TIEMPO REAL ---
    conn = obtener_conexion()
    productos = []
    if conn:
        cursor = conn.cursor()
        # Traemos solo los productos activos (Estado = 1)
        cursor.execute("SELECT Id, Codigo, Nombre, Descripcion, Precio, Stock FROM Productos WHERE Estado = True")
        rows = cursor.fetchall()
        # Convertimos a diccionarios para manejarlos fácil en el HTML
        for r in rows:
            productos.append({
                'id': r[0],
                'codigo': r[1],
                'nombre': r[2],
                'descripcion': r[3],
                'precio': r[4],
                'stock': r[5]
            })
        conn.close()
    # --------------------------------------------

    return render_template('dashboard.html', 
                           usuario=session.get('full_name'), 
                           rol=session.get('rol'),
                           productos=productos) # Enviamos la lista de productos

if __name__ == '__main__':
    app.run(debug=True)

