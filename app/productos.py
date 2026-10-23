"""
HU-01: Registrar un producto nuevo.
HU-02: Ver el listado de productos y  buscar uno.
HU-03: Dar de baja un producto.
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
    Solo muestra productos que est'en activos: Los dados de baja (HU-03) no aparecen.
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

# HU-02: Editar producto
# CA: El cambio se ve en el listado. SIn campos vacios ni SKU repetido

def buscar_producto_activo(conexion, sku):
    """
    Devuelve (id, sku, nombre, categoria, stock_minimo) del producto activo
    con ese código, o None si no existe o está dado de baja.
    """
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, sku, nombre, categoria, stock_minimo FROM productos "
        "WHERE sku = %s AND activo = 1",
        (sku,),
    )
    fila = cursor.fetchone()
    cursor.close()
    return fila


def sku_usado_por_otro(conexion, sku, producto_id):
    """
    True si OTRO producto (distinto de producto_id) ya usa ese código.
    Revisa también los dados de baja, porque el SKU es UNIQUE en la BD.
    """
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id FROM productos WHERE sku = %s AND id <> %s",
        (sku, producto_id),
    )
    fila = cursor.fetchone()
    cursor.close()
    return fila is not None


def editar_producto(conexion, sku_actual, nuevo_sku, nombre, categoria, stock_minimo):
    """
    Cambia el código, nombre, categoría y stock mínimo de un producto.
    El stock actual NO se edita aquí: solo cambia con entradas y salidas.
    Devuelve (True, mensaje) si se guardó, o (False, motivo) si no.
    """
    if not nuevo_sku or not nombre or not categoria:
        return False, "No se permiten campos vacíos: código, nombre y categoría son obligatorios."
    if stock_minimo is None:
        return False, "No se permiten campos vacíos: el stock mínimo es obligatorio."
    if stock_minimo < 0:
        return False, "El stock mínimo no puede ser negativo."

    producto = buscar_producto_activo(conexion, sku_actual)
    if producto is None:
        return False, f"No existe un producto activo con el código {sku_actual}."
    producto_id = producto[0]

    if sku_usado_por_otro(conexion, nuevo_sku, producto_id):
        return False, f"Ya existe otro producto con el código {nuevo_sku}."

    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE productos SET sku = %s, nombre = %s, categoria = %s, stock_minimo = %s "
        "WHERE id = %s",
        (nuevo_sku, nombre, categoria, stock_minimo, producto_id),
    )
    conexion.commit()
    cursor.close()
    return True, f"Producto '{nombre}' actualizado correctamente."



# HU-03: Dar de baja producto
# CA: pide confirmación. Si se confirma, deja de aparecer en el listado;
#     si se cancela, no cambia nada.


def dar_de_baja_producto(conexion, sku, confirmado):
    """
    Marca el producto como dado de baja (activo = 0). No se borra de la BD
    para no perder su historial de movimientos.
    Si confirmado es False, no cambia nada.
    Devuelve (True, mensaje) o (False, motivo).
    """
    if not confirmado:
        return False, "Operación cancelada. No se hizo ningún cambio."

    producto = buscar_producto_activo(conexion, sku)
    if producto is None:
        return False, f"No existe un producto activo con el código {sku}."
    producto_id, _, nombre, _, _ = producto

    cursor = conexion.cursor()
    cursor.execute("UPDATE productos SET activo = 0 WHERE id = %s", (producto_id,))
    conexion.commit()
    cursor.close()
    return True, f"Producto '{nombre}' dado de baja. Ya no aparecerá en el listado."


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


def pedir_texto_o_actual(mensaje, actual):
    """Pide un texto; si se deja vacío (Enter), se mantiene el valor actual."""
    texto = input(f"{mensaje} [{actual}]: ").strip()
    return texto if texto else actual


def pantalla_editar():
    print("\n--- Editar producto ---")
    sku_actual = input("Código (SKU) del producto a editar: ").strip()
    conexion = obtener_conexion()
    producto = buscar_producto_activo(conexion, sku_actual)
    if producto is None:
        conexion.close()
        print(f"ERROR: No existe un producto activo con el código {sku_actual}.")
        return

    _, sku, nombre, categoria, stock_minimo = producto
    print("Escribe el dato nuevo, o presiona Enter para dejar el actual.")
    nuevo_sku = pedir_texto_o_actual("Código (SKU)", sku)
    nuevo_nombre = pedir_texto_o_actual("Nombre", nombre)
    nueva_categoria = pedir_texto_o_actual("Categoría", categoria or "")
    texto_minimo = input(f"Stock mínimo [{stock_minimo}]: ").strip()
    if texto_minimo == "":
        nuevo_minimo = stock_minimo
    else:
        try:
            nuevo_minimo = int(texto_minimo)
        except ValueError:
            nuevo_minimo = None

    ok, mensaje = editar_producto(conexion, sku, nuevo_sku, nuevo_nombre,
                                  nueva_categoria, nuevo_minimo)
    conexion.close()
    print(("OK: " if ok else "ERROR: ") + mensaje)


def pantalla_baja():
    print("\n--- Dar de baja producto ---")
    sku = input("Código (SKU) del producto a dar de baja: ").strip()
    conexion = obtener_conexion()
    producto = buscar_producto_activo(conexion, sku)
    if producto is None:
        conexion.close()
        print(f"ERROR: No existe un producto activo con el código {sku}.")
        return

    nombre = producto[2]
    respuesta = input(f"¿Seguro que quieres dar de baja '{nombre}'? (s/n): ").strip().lower()
    confirmado = respuesta == "s"
    ok, mensaje = dar_de_baja_producto(conexion, sku, confirmado)
    conexion.close()
    print(("OK: " if ok else "ERROR: ") + mensaje)
