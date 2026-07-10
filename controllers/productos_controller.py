# controllers/productos_controller.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, session
from database.conexion import obtener_conexion

productos_blueprint = Blueprint('productos', __name__, url_prefix='/productos')
CARPETA_IMAGENES = os.path.join('static', 'img')

def procesar_imagen(file_input, codigo_producto, imagen_actual=None):
    if file_input and file_input.filename != '':
        _, ext = os.path.splitext(file_input.filename)
        nombre_archivo = f"{codigo_producto}{ext.lower()}"
        os.makedirs(CARPETA_IMAGENES, exist_ok=True)
        ruta_completa = os.path.join(CARPETA_IMAGENES, nombre_archivo)
        file_input.save(ruta_completa)
        return nombre_archivo
    return imagen_actual

@productos_blueprint.route('/')
def listar_productos():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    conn = obtener_conexion()
    productos = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id, Codigo, Nombre, Descripcion, Precio, Stock, StockMinimo, Imagen 
            FROM Productos WHERE Estado = True ORDER BY Id DESC
        """)
        rows = cursor.fetchall()
        for r in rows:
            productos.append({
                'id': r[0], 'codigo': r[1], 'nombre': r[2], 'descripcion': r[3],
                'precio': r[4], 'stock': r[5], 'stock_minimo': r[6], 'imagen': r[7]
            })
        conn.close()
    return render_template('productos/productos.html', usuario=session.get('full_name'), rol=session.get('rol'), productos=productos)

@productos_blueprint.route('/guardar', methods=['POST'])
def guardar_producto():
    codigo = request.form.get('codigo').strip().upper()
    nombre = request.form.get('nombre').strip()
    descripcion = request.form.get('descripcion').strip()
    precio = float(request.form.get('precio'))
    stock = int(request.form.get('stock'))
    stock_minimo = int(request.form.get('stock_minimo', 5))
    
    archivo_imagen = request.files.get('imagen_file')
    nombre_imagen = procesar_imagen(archivo_imagen, codigo)

    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Productos (Codigo, Nombre, Descripcion, Precio, Stock, StockMinimo, Imagen, Estado, FechaCreacion) 
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, GETDATE())
            """, (codigo, nombre, descripcion, precio, stock, stock_minimo, nombre_imagen))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('productos.listar_productos'))

@productos_blueprint.route('/editar', methods=['POST'])
def editar_producto():
    id_producto = request.form.get('id')
    codigo = request.form.get('codigo').strip().upper()
    nombre = request.form.get('nombre').strip()
    descripcion = request.form.get('descripcion').strip()
    precio = float(request.form.get('precio'))
    stock = int(request.form.get('stock'))
    stock_minimo = int(request.form.get('stock_minimo'))
    imagen_actual = request.form.get('imagen_actual')

    archivo_imagen = request.files.get('imagen_file')
    nombre_imagen = procesar_imagen(archivo_imagen, codigo, imagen_actual)

    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Productos 
                SET Codigo = ?, Nombre = ?, Descripcion = ?, Precio = ?, Stock = ?, StockMinimo = ?, Imagen = ?, FechaModificacion = GETDATE() 
                WHERE Id = ?
            """, (codigo, nombre, descripcion, precio, stock, stock_minimo, nombre_imagen, id_producto))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('productos.listar_productos'))

@productos_blueprint.route('/eliminar/<int:id_producto>')
def eliminar_producto(id_producto):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Productos SET Estado = 0, FechaModificacion = GETDATE() WHERE Id = ?", (id_producto,))
        conn.commit()
        conn.close()
    return redirect(url_for('productos.listar_productos'))