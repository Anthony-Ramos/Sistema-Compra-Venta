# backend/modelos/modelo_compras.py
"""Modelo de Compras: consulta de compras y reportes."""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from backend.db import DB

@dataclass
class Compra:
    """Entidad Compra vinculada a las tablas 'compras' y 'detalle_compras'."""
    proveedor: str
    fecha: str
    producto: str
    cantidad: int
    precio_unitario: float
    estado: str
    total: float

    @staticmethod
    def _row_to_compra(row: Tuple) -> "Compra":
        """Convierte una tupla de BD en un objeto Compra."""
        return Compra(
            proveedor=row[0],
            fecha=str(row[1]),
            producto=row[2],
            cantidad=row[3],
            precio_unitario=float(row[4]),
            estado=row[5],
            total=float(row[6]),
        )

    # ==========================
    # MÉTODOS PÚBLICOS
    # ==========================

    @classmethod
    def obtener_todas(cls) -> List["Compra"]:
        """
        Devuelve todas las compras con información de proveedor y producto.
        """
        sql = """
        SELECT 
            pr.nombre       AS proveedor,
            c.fecha,
            p.nombre        AS producto,
            dc.cantidad,
            dc.precio_unitario,
            c.estado,
            c.total
        FROM compras c
        INNER JOIN proveedores pr     ON c.id_proveedor = pr.id_proveedor
        INNER JOIN detalle_compras dc ON c.id_compra = dc.id_compra
        INNER JOIN producto p         ON dc.id_producto = p.id_producto
        ORDER BY c.fecha DESC;
        """
        rows = DB.fetch_all(sql)
        return [cls._row_to_compra(row) for row in rows]

    @classmethod
    def buscar_por_proveedor(cls, nombre_proveedor: str) -> List["Compra"]:
        """
        Devuelve todas las compras de un proveedor específico.
        """
        sql = """
        SELECT 
            pr.nombre       AS proveedor,
            c.fecha,
            p.nombre        AS producto,
            dc.cantidad,
            dc.precio_unitario,
            c.estado,
            c.total
        FROM compras c
        INNER JOIN proveedores pr     ON c.id_proveedor = pr.id_proveedor
        INNER JOIN detalle_compras dc ON c.id_compra = dc.id_compra
        INNER JOIN producto p         ON dc.id_producto = p.id_producto
        WHERE pr.nombre ILIKE %s
        ORDER BY c.fecha DESC;
        """
        rows = DB.fetch_all(sql, (f"%{nombre_proveedor}%",))
        return [cls._row_to_compra(row) for row in rows]