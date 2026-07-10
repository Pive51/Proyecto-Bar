from flask import Flask, render_template, redirect, url_for, session
from database.conexion import obtener_conexion

from controllers.auth_controller import auth_blueprint
from controllers.usuarios_controller import usuarios_blueprint
from controllers.ventas_controller import ventas_blueprint
from controllers.productos_controller import productos_blueprint

app = Flask(__name__)
app.secret_key = "llave_secreta_bar_pos_ecuador_2026"

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(usuarios_blueprint)
app.register_blueprint(ventas_blueprint)
app.register_blueprint(productos_blueprint)


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth.login"))


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    productos = []

    conn = obtener_conexion()

    if conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                codigo,
                nombre,
                descripcion,
                precio,
                stock
            FROM productos
            WHERE estado = TRUE
            ORDER BY nombre
        """)

        rows = cursor.fetchall()

        for r in rows:
            productos.append({
                "id": r[0],
                "codigo": r[1],
                "nombre": r[2],
                "descripcion": r[3],
                "precio": float(r[4]),
                "stock": r[5]
            })

        cursor.close()
        conn.close()

    return render_template(
        "dashboard.html",
        usuario=session.get("full_name"),
        rol=session.get("rol"),
        productos=productos
    )


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)