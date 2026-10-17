"""
Configuración compartida de las pruebas. pytest carga este archivo solo.

Las pruebas usan una BD aparte, "inventario_pymes_test", para no tocar los
datos reales. Antes de CADA prueba la BD se vuelve a crear desde
db/inventario_pymes.sql, así todas parten con los mismos 4 productos.

Ejecutar desde la carpeta app/:
    pytest

Por defecto se conecta igual que la app (CONFIG de conexion.py).
Para usar otro servidor se pueden definir las variables de entorno
DB_HOST, DB_PORT, DB_USER y DB_PASSWORD (las usa el CI de GitHub).
"""
import os

import mysql.connector
import pytest

from conexion import CONFIG

# Nombre de la BD de prueba (distinta de la real)
BD_PRUEBA = "inventario_pymes_test"

# Ruta al script SQL oficial: está en ../db/ mirando desde esta carpeta
CARPETA_APP = os.path.dirname(os.path.abspath(__file__))
RUTA_SQL = os.path.join(CARPETA_APP, "..", "db", "inventario_pymes.sql")


def datos_servidor():
    """Datos para conectarse al servidor MySQL (sin elegir BD todavía)."""
    return {
        "host": os.getenv("DB_HOST", CONFIG["host"]),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", CONFIG["user"]),
        "password": os.getenv("DB_PASSWORD", CONFIG["password"]),
    }


def leer_script_sql():
    """Lee el .sql, lo cambia a la BD de prueba y lo devuelve como lista de sentencias."""
    with open(RUTA_SQL, encoding="utf-8") as archivo:
        texto = archivo.read()

    # El script crea y usa `inventario_pymes`: lo cambiamos por la BD de prueba
    texto = texto.replace("`inventario_pymes`", "`" + BD_PRUEBA + "`")

    # Quitamos las líneas de comentario (las que empiezan con --)
    lineas_utiles = []
    for linea in texto.splitlines():
        if not linea.strip().startswith("--"):
            lineas_utiles.append(linea)
    texto = "\n".join(lineas_utiles)

    # Cada sentencia termina en ";". Guardamos solo los pedazos que tienen texto
    sentencias = []
    for pedazo in texto.split(";"):
        if pedazo.strip() != "":
            sentencias.append(pedazo.strip())
    return sentencias


@pytest.fixture
def conexion():
    """
    Entrega una conexión a la BD de prueba recién creada.
    Cualquier prueba que tenga un parámetro llamado "conexion" la recibe.
    """
    # 1) Crear (o reiniciar) la BD de prueba con el script oficial
    servidor = mysql.connector.connect(**datos_servidor())
    cursor = servidor.cursor()
    for sentencia in leer_script_sql():
        cursor.execute(sentencia)
    servidor.commit()
    cursor.close()
    servidor.close()

    # 2) Abrir la conexión que usará la prueba
    con = mysql.connector.connect(database=BD_PRUEBA, **datos_servidor())

    yield con  # aquí se ejecuta la prueba

    # 3) Al terminar la prueba se cierra la conexión
    con.close()
