productos = []
movimientos_stock = []

# HU-01: Registrar producto
def registrar_producto():
    print("\nREGISTRAR NUEVO PRODUCTO")

    # Pedir datos al usuario
    codigo = input("Ingrese el código del producto: ").strip()
    nombre = input("Ingrese el nombre del producto: ").strip()
    precio = input("Ingrese el precio del producto: ").strip()

    if not codigo or not nombre or not precio:
        print("Error: Todos los campos son obligatorios. No se guardó el producto.")
        return

    for prod in productos:
        if prod["codigo"] == codigo:
            print(
                f"Error: El código '{codigo}' ya está registrado. No se puede duplicar."
            )
            return

    try:
        precio = float(precio)
    except ValueError:
        print("Error: El precio debe ser un número válido.")
        return

    nuevo_producto = {
        "codigo": codigo,
        "nombre": nombre,
        "precio": precio,
        "stock": 0,
    }
    productos.append(nuevo_producto)
    print(f"Producto '{nombre}' registrado exitosamente con stock inicial de 0.")



# HU-05: Entrada de stock
def entrada_stock():
    print("\n--- ENTRADA DE STOCK ---")

    if not productos:
        print("No hay productos registrados en el sistema.")
        return

    codigo_buscar = input(
        "Ingrese el código del producto que recibió stock: "
    ).strip()

    producto_encontrado = None
    for prod in productos:
        if prod["codigo"] == codigo_buscar:
            producto_encontrado = prod
            break

    if not producto_encontrado:
        print(f"Error: El producto con código '{codigo_buscar}' no existe.")
        return

    cantidad_ingreso = input(
        f"¿Cuántas unidades llegaron de '{producto_encontrado['nombre']}'?: "
    ).strip()

    try:
        cantidad = int(cantidad_ingreso)
        if cantidad <= 0:
            print("Error: La cantidad debe ser mayor a cero.")
            return
    except ValueError:
        print("Error: Debe ingresar un número entero válido.")
        return

    producto_encontrado["stock"] += cantidad

    movimiento = {
        "codigo_producto": codigo_buscar,
        "tipo": "Entrada",
        "cantidad": cantidad,
    }
    movimientos_stock.append(movimiento)

    print(
        f"Stock actualizado. Nuevo stock de '{producto_encontrado['nombre']}': {producto_encontrado['stock']}"
    )

def menu():
    while True:
        print("\nSISTEMA DE INVENTARIO")
        print("1. Registrar producto (HU-01)")
        print("2. Entrada de stock (HU-05)")
        print("3. Ver productos actuales (Auxiliar)")
        print("4. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_producto()
        elif opcion == "2":
            entrada_stock()
        elif opcion == "3":
            print("\nLISTA DE PRODUCTOS")
            for p in productos:
                print(
                    f"Código: {p['codigo']} | Nombre: {p['nombre']} | Precio: ${p['precio']} | Stock: {p['stock']}"
                )
        elif opcion == "4":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()