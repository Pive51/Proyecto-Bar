# controllers/ventas_controller.py

from flask import Blueprint, request, jsonify, session
from database.conexion import obtener_conexion

ventas_blueprint = Blueprint("ventas", __name__, url_prefix="/ventas")


@ventas_blueprint.route("/registrar", methods=["POST"])
def registrar_venta():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Sesión expirada o no válida"
        }), 401

    datos = request.get_json()

    cliente = datos.get("cliente", "CONSUMIDOR FINAL")
    carrito = datos.get("carrito", [])
    id_usuario = session["user_id"]

    if not carrito:
        return jsonify({
            "success": False,
            "message": "El carrito está vacío"
        }), 400

    conn = obtener_conexion()

    if conn is None:
        return jsonify({
            "success": False,
            "message": "Error de conexión"
        }), 500

    cursor = conn.cursor()

    try:

        total_venta = sum(
            float(item["precio"]) * int(item["cantidad"])
            for item in carrito
        )

        subtotal_venta = total_venta

        # ===========================
        # CABECERA DE VENTA
        # ===========================

        query_venta = """
            INSERT INTO ventas
            (
                cliente,
                fecha,
                subtotal,
                descuento,
                total,
                id_usuario
            )
            VALUES
            (
                %s,
                NOW(),
                %s,
                0,
                %s,
                %s
            )
            RETURNING id;
        """

        cursor.execute(
            query_venta,
            (
                cliente,
                subtotal_venta,
                total_venta,
                id_usuario
            )
        )

        id_venta = cursor.fetchone()[0]

        print(f"Venta creada: {id_venta}")

        # ===========================
        # DETALLE
        # ===========================

        for item in carrito:

            id_producto = item["id"]
            cantidad = int(item["cantidad"])

            cursor.execute(
                """
                SELECT
                    precio,
                    stock
                FROM productos
                WHERE id=%s
                """,
                (id_producto,)
            )

            producto = cursor.fetchone()

            if producto is None:
                raise Exception(
                    f"No existe el producto {id_producto}"
                )

            precio_unitario = float(producto[0])
            stock_actual = int(producto[1])

            if stock_actual < cantidad:
                raise Exception(
                    f"Stock insuficiente del producto {id_producto}"
                )

            total_linea = precio_unitario * cantidad

            cursor.execute(
                """
                INSERT INTO detalle_venta
                (
                    id_venta,
                    id_producto,
                    cantidad,
                    precio_unitario,
                    total
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    id_venta,
                    id_producto,
                    cantidad,
                    precio_unitario,
                    total_linea
                )
            )

            cursor.execute(
                """
                UPDATE productos
                SET stock = stock - %s
                WHERE id = %s
                """,
                (
                    cantidad,
                    id_producto
                )
            )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Venta registrada correctamente."
        })

    except Exception as e:

        conn.rollback()

        print(e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        conn.close()