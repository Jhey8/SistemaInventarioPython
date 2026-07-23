"""Carga schema.sql en la base MySQL de Aiven. Ejecutar una sola vez:
       python cargar_schema_aiven.py
   Pide los datos de conexion de Aiven y crea todas las tablas."""

import os

import mysql.connector

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

host = input("Host de Aiven (termina en .aivencloud.com): ").strip()
puerto = int(input("Puerto (ej. 22205): ").strip())
usuario = input("Usuario [avnadmin]: ").strip() or "avnadmin"
password = input("Password de la BD (se vera al escribir): ").strip()
nombre_bd = input("Base de datos [inventario]: ").strip() or "inventario"

with open(RUTA, encoding="utf-8") as f:
    contenido = f.read()

# Se separan las sentencias por ';' y se descartan las de crear/usar la base
# (la base ya existe en Aiven; se selecciona con USE mas abajo).
sentencias = []
for bruta in contenido.split(";"):
    s = bruta.strip()
    if not s:
        continue
    inicio = s.upper()
    if inicio.startswith("CREATE DATABASE") or inicio.startswith("USE "):
        continue
    sentencias.append(s)

conn = mysql.connector.connect(host=host, port=puerto, user=usuario, password=password)
cur = conn.cursor()

try:
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {nombre_bd}")
except mysql.connector.Error as e:
    print(f"Aviso: no se pudo crear la base ({e}). Debe existir ya en Aiven.")

cur.execute(f"USE {nombre_bd}")
for sentencia in sentencias:
    cur.execute(sentencia)
conn.commit()
cur.close()
conn.close()

print(f"OK: {len(sentencias)} sentencias ejecutadas en la base '{nombre_bd}'.")
