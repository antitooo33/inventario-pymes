"""
HU-01: Registrar un producto nuevo.
HU-04: Ver el listado de productos y buscar uno.
"""
from conexion import obtener_conexion



def existe_sku(conexion, sku):
    """True si ya hay un producto con ese código (SKU)."""
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM productos WHERE sku = %s", (sku,))
    fila = cursor.fetchone()
    cursor.close()
    return fila is not None


def registrar_producto(conexion, sku, nombre, categoria, stock_inicial, stock_minimo):
    """
    Guarda un producto nuevo.
    Devuelve (True, mensaje) si se guardó, o (False, motivo) si no.
    """
    if not sku or not nombre or not categoria:
        return False, "Faltan datos: nombre, código y categoría son obligatorios."
    if stock_inicial is None or stock_minimo is None:
        return False, "Faltan datos: stock inicial y stock mínimo son obligatorios."
    if stock_inicial < 0 or stock_minimo < 0:
        return False, "El stock no puede ser negativo."

    if existe_sku(conexion, sku):
        return False, f"Ya existe un producto con el código {sku}."

    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO productos (sku, nombre, categoria, stock_actual, stock_minimo) "
        "VALUES (%s, %s, %s, %s, %s)",
        (sku, nombre, categoria, stock_inicial, stock_minimo),
    )
    conexion.commit()
    cursor.close()
    return True, f"Producto '{nombre}' registrado correctamente."


def listar_productos(conexion, busqueda=""):
    """
    Devuelve una lista de productos.
    Si 'busqueda' tiene texto, filtra por nombre o por código (SKU).
    Cada producto es una tupla: (sku, nombre, categoria, stock_actual, stock_minimo)
    """
    cursor = conexion.cursor()
    consulta = "SELECT sku, nombre, categoria, stock_actual, stock_minimo FROM productos"
    if busqueda:
        consulta += " WHERE nombre LIKE %s OR sku LIKE %s"
        patron = f"%{busqueda}%"
        cursor.execute(consulta + " ORDER BY nombre", (patron, patron))
    else:
        cursor.execute(consulta + " ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas



def pedir_entero(mensaje):
    """Pide un número entero; devuelve None si se deja vacío o no es número."""
    texto = input(mensaje).strip()
    if texto == "":
        return None
    try:
        return int(texto)
    except ValueError:
        return None

def mostrar_tabla(productos):
    if not productos:
        print("No se encontraron productos.")
        return
    print(f"\n{'CÓDIGO':<12}{'NOMBRE':<25}{'CATEGORÍA':<18}{'STOCK':>7}{'MÍNIMO':>8}")
    print("-" * 70)
    for sku, nombre, categoria, stock, minimo in productos:
        aviso = "  <- bajo mínimo" if stock < minimo else ""
        print(f"{sku:<12}{nombre:<25}{categoria or 'sin categoría':<18}{stock:>7}{minimo:>8}{aviso}")
    print()

def pantalla_registrar():
    print("\n--- Registrar producto nuevo ---")
    sku = input("Código (SKU): ").strip()
    nombre = input("Nombre: ").strip()
    categoria = input("Categoría: ").strip()
    stock_inicial = pedir_entero("Stock inicial: ")
    stock_minimo = pedir_entero("Stock mínimo: ")

    conexion = obtener_conexion()
    ok, mensaje = registrar_producto(conexion, sku, nombre, categoria, stock_inicial, stock_minimo)
    conexion.close()
    print(("OK: " if ok else "ERROR: ") + mensaje)

def pantalla_listado():
    print("\n--- Listado de productos ---")
    busqueda = input("Buscar por nombre o código (Enter para ver todos): ").strip()
    conexion = obtener_conexion()
    productos = listar_productos(conexion, busqueda)
    conexion.close()
    mostrar_tabla(productos)