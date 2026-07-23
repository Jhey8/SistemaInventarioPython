import mysql.connector
from mysql.connector import pooling

from config import DB_CONFIG

TAMANO_POOL = 5
_pool = None

def _crear_pool():
    return pooling.MySQLConnectionPool(
        pool_name="inventario_pool",
        pool_size=TAMANO_POOL,
        pool_reset_session=True,
        **DB_CONFIG,
    )

def get_connection():
    """Devuelve una conexion del pool. Reutilizar conexiones evita rehacer el
    saludo TLS y la autenticacion en cada consulta (clave con una BD remota).
    Si una conexion quedo inservible (la BD cerro la sesion por inactividad),
    se reconecta o se recrea el pool."""
    global _pool
    if _pool is None:
        _pool = _crear_pool()
    try:
        conn = _pool.get_connection()
    except mysql.connector.Error:
        _pool = _crear_pool()
        conn = _pool.get_connection()

    try:
        if not conn.is_connected():
            conn.reconnect(attempts=2, delay=1)
    except Exception:
        pass
    return conn
