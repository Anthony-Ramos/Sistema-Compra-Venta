from typing import List, Dict
from backend.db import DB

class Categoria:
    """Modelo para la entidad 'categoria_producto'."""

    @staticmethod
    def agregar(nombre: str) -> int:
        """Agrega una categoría y devuelve su ID."""
        # Verificar si ya existe (ignorando mayúsculas/minúsculas)
        existente = DB.fetch_one(
            "SELECT id_categoria FROM categoria_producto WHERE LOWER(nombre) = LOWER(%s)",
            (nombre,)
        )
        if existente:
            raise ValueError("La categoría ya existe")

        # Insertar nueva categoría
        row = DB.execute_returning(
            "INSERT INTO categoria_producto(nombre) VALUES(%s) RETURNING id_categoria",
            (nombre,)
        )
        return int(row[0])

    @staticmethod
    def listar() -> List[Dict]:
        """Devuelve todas las categorías como lista de diccionarios."""
        rows = DB.fetch_all(
            "SELECT id_categoria AS id, nombre FROM categoria_producto ORDER BY id_categoria"
        )
        return [{"id": r[0], "nombre": r[1]} for r in rows]

    @staticmethod
    def eliminar(id_categoria: int):
        """Elimina una categoría por ID."""
        DB.execute("DELETE FROM categoria_producto WHERE id_categoria=%s", (id_categoria,))

    @staticmethod
    def editar(id_categoria: int, nombre: str):
        """Edita el nombre de una categoría por ID."""
        DB.execute(
            "UPDATE categoria_producto SET nombre=%s WHERE id_categoria=%s",
            (nombre, id_categoria)
        )