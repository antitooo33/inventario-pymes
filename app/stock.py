"""
HU-05: Sumar stock cuando llega mercadería (entrada).
HU-06: Restar stock cuando se vende algo, sin quedar en negativo (salida).
"""
from datetime import datetime

from conexion import obtener_conexion

def buscar_por_sku(conexion, sku):
    """Devuelve (id, nombre, stock_actual) del producto, o None si no existe."""
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, stock_actual FROM productos WHERE sku = %s", (sku,))
    fila = cursor.fetchone()
    cursor.close()
    return fila

def guardar_movimiento(cursor, producto_id, tipo, cantidad):
    """Registra el movimiento con la fecha y hora actual."""
    cursor.execute(
        "INSERT INTO movimientos (producto_id, tipo, cantidad, fecha) VALUES (%s, %s, %s, %s)",
        (producto_id, tipo, cantidad, datetime.now()),
    )

def entrada_stock(conexion, sku, cantidad):
    """
    Suma 'cantidad' al stock del producto y guarda el movimiento.
    Devuelve (True, mensaje) o (False, motivo).
    """
    if cantidad is None or cantidad <= 0:
        return False, "La cantidad debe ser un número mayor que 0."

    producto = buscar_por_sku(conexion, sku)
    if producto is None:
        return False, f"No existe un producto con el código {sku}."
    producto_id, nombre, stock_actual = producto

    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE productos SET stock_actual = stock_actual + %s WHERE id = %s",
            (cantidad, producto_id),
        )
        guardar_movimiento(cursor, producto_id, "entrada", cantidad)
        conexion.commit()   # se guardan los dos cambios juntos
    except Exception:
        conexion.rollback()  # si algo falla, no se guarda nada
        raise
    finally:
        cursor.close()

    nuevo = stock_actual + cantidad
    return True, f"Entrada registrada. '{nombre}': {stock_actual} -> {nuevo} unidades."

def salida_stock(conexion, sku, cantidad):
    """
    Resta 'cantidad' al stock sin dejarlo en negativo y guarda el movimiento.
    Devuelve (True, mensaje) o (False, motivo).
    """
    if cantidad is None or cantidad <= 0:
        return False, "La cantidad debe ser un número mayor que 0."

    producto = buscar_por_sku(conexion, sku)
    if producto is None:
        return False, f"No existe un producto con el código {sku}."
    producto_id, nombre, stock_actual = producto
    if cantidad > stock_actual:
        return False, (f"No hay stock suficiente. '{nombre}' tiene {stock_actual} "
                       f"unidades y se intentó sacar {cantidad}. El stock no cambió.")

    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE productos SET stock_actual = stock_actual - %s "
            "WHERE id = %s AND stock_actual >= %s",
            (cantidad, producto_id, cantidad),
        )
        if cursor.rowcount == 0:
            conexion.rollback()
            return False, "No hay stock suficiente. El stock no cambió."
        guardar_movimiento(cursor, producto_id, "salida", cantidad)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()

    nuevo = stock_actual - cantidad
    return True, f"Salida registrada. '{nombre}': {stock_actual} -> {nuevo} unidades."

def pedir_cantidad():
    texto = input("Cantidad: ").strip()
    try:
        return int(texto)
    except ValueError:
        return None

def pantalla_entrada():
    print("\n--- Entrada de stock (llegó mercadería) ---")
    sku = input("Código (SKU) del producto: ").strip()
    cantidad = pedir_cantidad()
    conexion = obtener_conexion()
    ok, mensaje = entrada_stock(conexion, sku, cantidad)
    conexion.close()
    print(("OK: " if ok else "ERROR: ") + mensaje)

def pantalla_salida():
    print("\n--- Salida de stock (venta) ---")
    sku = input("Código (SKU) del producto: ").strip()
    cantidad = pedir_cantidad()
    conexion = obtener_conexion()
    ok, mensaje = salida_stock(conexion, sku, cantidad)
    conexion.close()
    print(("OK: " if ok else "ERROR: ") + mensaje)