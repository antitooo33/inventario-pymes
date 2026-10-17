"""
Conexión de Python a MySQL.
Todos los demás archivos usan obtener_conexion() para hablar con la base de datos.

Requisito:  pip install mysql-connector-python
"""
import mysql.connector

CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "inventario_pymes",
}

def obtener_conexion():
    """Devuelve una conexión abierta a la base de datos."""
    return mysql.connector.connect(**CONFIG)
