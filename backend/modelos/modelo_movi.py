# backend/modelos/modelo_movi.py
"""Modelo de Movimientos (compras + ventas) del mes actual."""

from dataclasses import dataclass
from typing import List, Tuple
from backend.db import DB

@dataclass
class Movimiento:
    """Movimiento unificado de COMPRA o VENTA."""
    tipo: str               # 'COMPRA' | 'VENTA'
    fecha: str              # fecha del movimiento
    id_producto: int
    producto: str
    cantidad: int
    precio_unitario: float
    total_linea: float
    contraparte: str        # proveedor (compra) o usuario (venta)
    id_movimiento: int      # id_compra o id_venta, según tipo

    @staticmethod
    def _row_to_mov(row: Tuple) -> "Movimiento":
        return Movimiento(
            tipo=row[0],
            fecha=str(row[1]),
            id_producto=int(row[2]),
            producto=row[3],
            cantidad=int(row[4]),
            precio_unitario=float(row[5]),
            total_linea=float(row[6]),
            contraparte=row[7],
            id_movimiento=int(row[8]),
        )

    # ==========================
    # MÉTODOS PÚBLICOS
    # ==========================
    @classmethod
    def obtener_mes_actual(cls) -> List["Movimiento"]:
        """
        Devuelve todos los movimientos (compras + ventas) del mes actual.
        """
        sql = """
        SELECT
          'COMPRA' AS tipo,
          c.fecha,
          p.id_producto,
          p.nombre        AS producto,
          dc.cantidad,
          dc.precio_unitario,
          (dc.cantidad * dc.precio_unitario) AS total_linea,
          pr.nombre       AS contraparte,     -- proveedor
          c.id_compra     AS id_movimiento
        FROM detalle_compras dc
        JOIN compras      c  ON c.id_compra   = dc.id_compra
        JOIN producto     p  ON p.id_producto = dc.id_producto
        LEFT JOIN proveedores pr ON pr.id_proveedor = c.id_proveedor
        WHERE c.fecha >= date_trunc('month', CURRENT_DATE)
          AND c.fecha <  (date_trunc('month', CURRENT_DATE) + INTERVAL '1 month')

        UNION ALL

        SELECT
          'VENTA'  AS tipo,
          v.fecha,
          p.id_producto,
          p.nombre        AS producto,
          dv.cantidad,
          dv.precio_unitario,
          (dv.cantidad * dv.precio_unitario) AS total_linea,
          u.nom_usuario   AS contraparte,     -- usuario que registró la venta
          v.id_venta      AS id_movimiento
        FROM detalle_ventas dv
        JOIN ventas      v  ON v.id_venta    = dv.id_venta
        JOIN producto    p  ON p.id_producto = dv.id_producto
        JOIN usuarios    u  ON u.id_usuario  = v.id_usuario
        WHERE v.fecha >= date_trunc('month', CURRENT_DATE)
          AND v.fecha <  (date_trunc('month', CURRENT_DATE) + INTERVAL '1 month')
        ORDER BY fecha, tipo, id_producto;
        """
        rows = DB.fetch_all(sql)
        return [cls._row_to_mov(r) for r in rows]