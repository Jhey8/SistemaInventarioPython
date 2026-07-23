from repositories.database import get_connection
from models.perfil import crear_perfil

class PerfilRepository:
    def _ids_modulos(self, cursor, id_perfil):
        cursor.execute(
            "SELECT id_modulo FROM perfil_modulo WHERE id_perfil = %s", (id_perfil,)
        )
        return [fila["id_modulo"] for fila in cursor.fetchall()]

    def _fila_a_perfil(self, cursor, fila):
        datos = dict(fila)
        datos["modulos"] = self._ids_modulos(cursor, datos["id_perfil"])
        return crear_perfil(datos)

    def listar(self, solo_activos=False):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            filtro = " WHERE estado = 1" if solo_activos else " WHERE estado <> 2"
            cursor.execute("SELECT * FROM perfiles" + filtro + " ORDER BY nombre")
            filas = cursor.fetchall()
            return [self._fila_a_perfil(cursor, f) for f in filas]
        finally:
            cursor.close()
            conn.close()

    def obtener(self, id_perfil):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM perfiles WHERE id_perfil = %s", (id_perfil,))
            fila = cursor.fetchone()
            return self._fila_a_perfil(cursor, fila) if fila else None
        finally:
            cursor.close()
            conn.close()

    def buscar_por_nombre(self, nombre):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM perfiles WHERE nombre = %s", (nombre,))
            fila = cursor.fetchone()
            return crear_perfil(dict(fila, modulos=[])) if fila else None
        finally:
            cursor.close()
            conn.close()

    def agregar(self, perfil):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO perfiles (nombre, descripcion) VALUES (%s, %s)",
                (perfil.nombre, perfil.descripcion),
            )
            perfil.id_perfil = cursor.lastrowid
            self._guardar_modulos(cursor, perfil.id_perfil, perfil.modulos)
            conn.commit()
            return perfil
        finally:
            cursor.close()
            conn.close()

    def actualizar(self, perfil):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE perfiles SET nombre = %s, descripcion = %s WHERE id_perfil = %s",
                (perfil.nombre, perfil.descripcion, perfil.id_perfil),
            )
            cursor.execute(
                "DELETE FROM perfil_modulo WHERE id_perfil = %s", (perfil.id_perfil,)
            )
            self._guardar_modulos(cursor, perfil.id_perfil, perfil.modulos)
            conn.commit()
            return perfil
        finally:
            cursor.close()
            conn.close()

    def eliminar(self, id_perfil):
        self.cambiar_estado(id_perfil, 2)

    def cambiar_estado(self, id_perfil, estado):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE perfiles SET estado = %s WHERE id_perfil = %s",
                (int(estado), id_perfil),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def _guardar_modulos(self, cursor, id_perfil, modulos):
        for id_modulo in modulos:
            cursor.execute(
                "INSERT INTO perfil_modulo (id_perfil, id_modulo) VALUES (%s, %s)",
                (id_perfil, id_modulo),
            )
