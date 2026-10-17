
from conexion import conectar


def listar_productos():
    conexion = conectar()

    if conexion is None:
        return

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT sku, nombre, categoria, stock_actual, stock_minimo
        FROM productos
        ORDER BY nombre
    """)

    productos = cursor.fetchall()
    mostrar_productos(productos)

    cursor.close()
    conexion.close()


def buscar_productos():
    termino = input("Ingresa el nombre o codigo del producto: ").strip()

    if not termino:
        print("Debes ingresar un nombre o codigo.")
        return

    conexion = conectar()

    if conexion is None:
        return

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT sku, nombre, categoria, stock_actual, stock_minimo
        FROM productos
        WHERE nombre LIKE %s OR sku LIKE %s
        ORDER BY nombre
    """, (f"%{termino}%", f"%{termino}%"))

    productos = cursor.fetchall()
    mostrar_productos(productos)

    cursor.close()
    conexion.close()


def mostrar_productos(productos):
    if not productos:
        print("\nNo se encontraron productos.")
        return

    print("\nListado de Productos")

    for producto in productos:
        print(f"""
Codigo: {producto['sku']}
Nombre: {producto['nombre']}
Categoria: {producto['categoria'] or 'Sin categoria'}
Stock actual: {producto['stock_actual']}
Stock minimo: {producto['stock_minimo']}
----------------------------
""")


def menu():
    while True:
        print("\nInventario Pymes")
        print("1. Ver todos los productos")
        print("2. Buscar producto por nombre o codigo")
        print("0. Salir")

        opcion = input("Selecciona una opcion: ").strip()

        if opcion == "1":
            listar_productos()
        elif opcion == "2":
            buscar_productos()
        elif opcion == "0":
            print("Saliendo del menu...")
            break
        else:
            print("Opcion no valida. Intenta nuevamente.")


if __name__ == "__main__":
    menu()
