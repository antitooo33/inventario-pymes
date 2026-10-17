"""
Pruebas de HU-01 (registrar producto) y HU-04 (listado y búsqueda).

Cada prueba recibe "conexion" (ver conftest.py): una BD de prueba recién
creada con estos 4 productos:

    SKU-001  Arroz grado 1 1kg       Abarrotes  stock 20  mínimo 5
    SKU-002  Café molido 250g        Abarrotes  stock 5   mínimo 3
    SKU-003  Detergente líquido 3L   Limpieza   stock 2   mínimo 4
    SKU-004  Cuaderno universitario  Librería   stock 10  mínimo 10
"""
from productos import registrar_producto, listar_productos


def cantidad_de_productos(conexion):
    """Cuántos productos hay en total en la BD."""
    return len(listar_productos(conexion))


# ---------------------------------------------------------------
# HU-01: Registrar producto
# CA: pide nombre, SKU, categoría, stock inicial y stock mínimo.
#     No guarda si falta un dato o si el SKU ya existe.
# ---------------------------------------------------------------

def test_registrar_producto_con_todos_los_datos(conexion):
    ok, mensaje = registrar_producto(conexion, "SKU-100", "Azúcar 1kg", "Abarrotes", 12, 4)

    assert ok is True
    # El producto nuevo debe aparecer en el listado con sus datos
    encontrados = listar_productos(conexion, "SKU-100")
    assert encontrados == [("SKU-100", "Azúcar 1kg", "Abarrotes", 12, 4)]


def test_no_guarda_si_falta_el_sku(conexion):
    ok, mensaje = registrar_producto(conexion, "", "Azúcar 1kg", "Abarrotes", 12, 4)

    assert ok is False
    assert cantidad_de_productos(conexion) == 4  # siguen los 4 de siempre


def test_no_guarda_si_falta_el_nombre(conexion):
    ok, mensaje = registrar_producto(conexion, "SKU-100", "", "Abarrotes", 12, 4)

    assert ok is False
    assert cantidad_de_productos(conexion) == 4


def test_no_guarda_si_falta_la_categoria(conexion):
    ok, mensaje = registrar_producto(conexion, "SKU-100", "Azúcar 1kg", "", 12, 4)

    assert ok is False
    assert cantidad_de_productos(conexion) == 4


def test_no_guarda_si_falta_el_stock_inicial(conexion):
    # None es lo que entrega pedir_entero() cuando se deja vacío
    ok, mensaje = registrar_producto(conexion, "SKU-100", "Azúcar 1kg", "Abarrotes", None, 4)

    assert ok is False
    assert cantidad_de_productos(conexion) == 4


def test_no_guarda_si_falta_el_stock_minimo(conexion):
    ok, mensaje = registrar_producto(conexion, "SKU-100", "Azúcar 1kg", "Abarrotes", 12, None)

    assert ok is False
    assert cantidad_de_productos(conexion) == 4


def test_no_guarda_si_el_sku_ya_existe(conexion):
    # SKU-001 ya es el arroz
    ok, mensaje = registrar_producto(conexion, "SKU-001", "Otro producto", "Abarrotes", 1, 1)

    assert ok is False
    assert cantidad_de_productos(conexion) == 4
    # El producto original no cambió
    encontrados = listar_productos(conexion, "SKU-001")
    assert encontrados[0][1] == "Arroz grado 1 1kg"


def test_sku_repetido_en_minusculas_tambien_se_rechaza(conexion):
    # La BD no distingue mayúsculas: "sku-001" choca con "SKU-001"
    ok, mensaje = registrar_producto(conexion, "sku-001", "Otro producto", "Abarrotes", 1, 1)

    assert ok is False
    assert cantidad_de_productos(conexion) == 4


def test_no_guarda_stock_negativo(conexion):
    ok, mensaje = registrar_producto(conexion, "SKU-100", "Azúcar 1kg", "Abarrotes", -5, 4)

    assert ok is False
    assert cantidad_de_productos(conexion) == 4


# ---------------------------------------------------------------
# HU-04: Listado y búsqueda
# CA: muestra todos los productos con su stock.
#     Busca por nombre o por SKU.
# ---------------------------------------------------------------

def test_listado_muestra_todos_los_productos_con_su_stock(conexion):
    productos = listar_productos(conexion)

    assert len(productos) == 4
    # Cada fila es (sku, nombre, categoria, stock_actual, stock_minimo)
    for sku, nombre, categoria, stock, minimo in productos:
        assert stock is not None


def test_buscar_por_parte_del_nombre(conexion):
    encontrados = listar_productos(conexion, "arroz")

    assert len(encontrados) == 1
    assert encontrados[0][0] == "SKU-001"


def test_buscar_sin_tilde_encuentra_con_tilde(conexion):
    # "cafe" debe encontrar "Café molido 250g"
    encontrados = listar_productos(conexion, "cafe")

    assert len(encontrados) == 1
    assert encontrados[0][0] == "SKU-002"


def test_buscar_por_sku(conexion):
    encontrados = listar_productos(conexion, "SKU-003")

    assert len(encontrados) == 1
    assert encontrados[0][1] == "Detergente líquido 3L"


def test_busqueda_sin_resultados_devuelve_lista_vacia(conexion):
    encontrados = listar_productos(conexion, "no existe esto")

    assert encontrados == []
