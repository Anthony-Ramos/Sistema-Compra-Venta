# backend/modelos/modelo_stockMin.py
"""Modelo de Stock Mínimo: productos con stock menor o igual a 30."""

from dataclasses import dataclass
from typing import List, Tuple
from backend.db import DB

@dataclass
class StockMinimo:
    """Entidad StockMinimo vinculada a la tabla 'producto'."""
    id_producto: int
    nombre: str
    descripcion: str
    stock_minimo: int

    @staticmethod
    def _row_to_stock(row: Tuple) -> "StockMinimo":
        """Convierte una tupla de BD en un objeto StockMinimo."""
        return StockMinimo(
            id_producto=row[0],
            nombre=row[1],
            descripcion=row[2],
            stock_minimo=row[3],
        )

    # ==========================
    # MÉTODOS PÚBLICOS
    # ==========================

    @classmethod
    def obtener_bajo_stock(cls) -> List["StockMinimo"]:
        """
        Devuelve todos los productos con stock menor o igual a 30.
        """
        sql = """
        SELECT 
            id_producto,
            nombre,
            descripcion,
            stock_minimo
        FROM producto
        WHERE stock_minimo <= 30
        ORDER BY stock_minimo ASC;
        """
        rows = DB.fetch_all(sql)
        return [cls._row_to_stock(row) for row in rows]