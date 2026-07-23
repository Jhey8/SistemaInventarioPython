from repositories.database import get_connection
from models.categoria import crear_categoria

class CategoriaRepository:
    def _fila_a_categoria(self, fila):
        return crear_categoria(dict(fila))

    def listar(self, solo_activos=False):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            filtro = " WHERE estado = 1" if solo_activos else " WHERE estado <> 2"
            cursor.execute("SELECT * FROM categorias" + filtro + " ORDER BY nombre")
            return [self._fila_a_categoria(f) for f in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def obtener(self, id):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categorias WHERE id = %s", (id,))
            fila = cursor.fetchone()
            return self._fila_a_categoria(fila) if fila else None
        finally:
            cursor.close()
            conn.close()

    def buscar_por_nombre(self, nombre):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categorias WHERE nombre = %s", (nombre,))
            fila = cursor.fetchone()
            return self._fila_a_categoria(fila) if fila else None
        finally:
            cursor.close()
            conn.close()

    def agregar(self, categoria):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
                (categoria.nombre, categoria.descripcion),
            )
            conn.commit()
            categoria.id = cursor.lastrowid
            return categoria
        finally:
            cursor.close()
            conn.close()

    def actualizar(self, categoria):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categorias SET nombre = %s, descripcion = %s WHERE id = %s",
                (categoria.nombre, categoria.descripcion, categoria.id),
            )
            conn.commit()
            return categoria
        finally:
            cursor.close()
            conn.close()

    def eliminar(self, id):
        self.cambiar_estado(id, 2)

    def cambiar_estado(self, id, estado):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categorias SET estado = %s WHERE id = %s", (int(estado), id)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
