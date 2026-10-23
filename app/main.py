"""
Inventario ligero para Pymes - Sprint 1
Ejecutar con:  python main.py
"""
from productos import pantalla_registrar, pantalla_listado, pantalla_editar, pantalla_baja
from stock import pantalla_entrada, pantalla_salida

def menu():
    while True:
        print("\nINVENTARIO PYMES")
        print("1. Registrar producto nuevo")
        print("2. Ver listado / buscar producto")
        print("3. Entrada de stock (llegó mercadería)")
        print("4. Salida de stock (venta)")
        print("5. Editar los datos de un producto")
        print("6. Dar de baja producto")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()

        try:
            if opcion == "1":
                pantalla_registrar()
            elif opcion == "2":
                pantalla_listado()
            elif opcion == "3":
                pantalla_entrada()
            elif opcion == "4":
                pantalla_salida()
            elif opcion == "5":
                pantalla_editar()
            elif opcion =="6":
                pantalla_baja()
            elif opcion == "0":
                print("Hasta luego.")
                break
            else:
                print("Opción no válida.")
        except Exception as error:
            print(f"Ocurrió un error con la base de datos: {error}")

if __name__ == "__main__":
    menu()
