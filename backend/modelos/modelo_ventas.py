# backend/modelos/modelo_ventas.py
"""Modelo de Ventas: consulta de ventas y reportes."""
from typing import Optional

from dataclasses import dataclass
from typing import List, Tuple, Optional
from backend.db import DB

@dataclass
class Venta:
    """Entidad Venta vinculada a las tablas 'ventas' y 'detalle_ventas'."""
    id_venta: int
    fecha: str
    usuario: str
    producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float
    total_venta: float
    metodo_pago: str

    @staticmethod
    def _row_to_venta(row: Tuple) -> "Venta":
        """Convierte una tupla de BD en un objeto Venta."""
        return Venta(
            id_venta=row[0],
            fecha=str(row[1]),
            usuario=row[2],
            producto=row[3],
            cantidad=row[4],
            precio_unitario=float(row[5]),
            subtotal=float(row[6]),
            total_venta=float(row[7]),
            metodo_pago=row[8],
        )

    # ===========================
    # MÉTODOS PÚBLICOS
    # ===========================

    @classmethod
    def total_todas(cls) -> float:
        """Suma total de todas las ventas."""
        row = DB.fetch_one("SELECT COALESCE(SUM(total), 0) FROM ventas")
        return float(row[0]) if row else 0.0

    @classmethod
    def total_por_mes(cls, mes_yyyy_mm: str) -> float:
        """
        Suma total de ventas para un mes específico (formato 'YYYY-MM').
        Usa rango [inicio, inicio + 1 mes).
        """
        inicio = f"{mes_yyyy_mm}-01"
        sql = """
            SELECT COALESCE(SUM(total), 0)
            FROM ventas
            WHERE fecha >= %s
              AND fecha < (%s::date + INTERVAL '1 month')
        """
        row = DB.fetch_one(sql, (inicio, inicio))
        return float(row[0]) if row else 0.0


    @classmethod
    def obtener_todas(cls) -> List["Venta"]:
        """
        Devuelve todas las ventas con información de usuario y producto.
        Usa DB.fetch_all -> retorna lista de tuplas.
        """
        sql = """
        SELECT 
            v.id_venta,
            v.fecha,
            u.nom_usuario,
            p.nombre AS nom_producto,
            dv.cantidad,
            dv.precio_unitario,
            (dv.cantidad * dv.precio_unitario) AS subtotal,
            v.total AS total_venta,
            v.metodo_pago
        FROM ventas v
        INNER JOIN usuarios u ON v.id_usuario = u.id_usuario
        INNER JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        INNER JOIN producto p ON dv.id_producto = p.id_producto
        ORDER BY v.id_venta DESC
        """
        rows = DB.fetch_all(sql)  # ← importante: devuelve tuplas
        return [cls._row_to_venta(row) for row in rows]

    @classmethod
    def buscar_por_id(cls, id_venta: int) -> Optional["Venta"]:
        """
        Devuelve una venta específica por ID (mismos alias que en obtener_todas).
        """
        sql = """
        SELECT 
            v.id_venta,
            v.fecha,
            u.nom_usuario,
            p.nombre AS nom_producto,
            dv.cantidad,
            dv.precio_unitario,
            (dv.cantidad * dv.precio_unitario) AS subtotal,
            v.total AS total_venta,
            v.metodo_pago
        FROM ventas v
        INNER JOIN usuarios u ON v.id_usuario = u.id_usuario
        INNER JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
        INNER JOIN producto p ON dv.id_producto = p.id_producto
        WHERE v.id_venta = %s
        """
        row = DB.fetch_one(sql, (id_venta,))
        return cls._row_to_venta(row) if row else None

    @classmethod
    def eliminar(cls, id_venta: int) -> None:
        """
        Elimina una venta (y sus detalles asociados).
        """
        DB.execute("DELETE FROM detalle_ventas WHERE id_venta = %s", (id_venta,))
        DB.execute("DELETE FROM ventas WHERE id_venta = %s", (id_venta,))
