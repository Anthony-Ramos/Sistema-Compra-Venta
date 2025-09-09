# categoriGra.py
# -*- coding: utf-8 -*-
"""
Modelo para obtener: id_categoria, nombre_categoria y total_productos,
listo para alimentar una gráfica (labels/values).

Requisitos:
- Haber llamado antes: DB.init_app(Config)
"""

from typing import List, Dict, Tuple
from db import DB

SQL_CATEGORIAS = """
SELECT
  c.id_categoria,
  c.nombre            AS nombre_categoria,
  COUNT(p.id_producto) AS total_productos
FROM categoria_producto AS c
LEFT JOIN producto AS p
  ON p.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nombre
ORDER BY c.id_categoria;
"""

def fetch_categoria_counts() -> List[Dict]:
    """
    Retorna una lista de diccionarios:
    [
      {"id_categoria": 1, "nombre_categoria": "Bebidas", "total_productos": 12},
      ...
    ]
    """
    rows = DB.ejecutar_consulta(SQL_CATEGORIAS, fetch_all=True) or []
    # Normalizamos tipos (total_productos a int)
    for r in rows:
        r["total_productos"] = int(r.get("total_productos") or 0)
    return rows

def data_for_chart() -> Tuple[List[str], List[int]]:
    """
    Devuelve (labels, values) para tu librería de gráficas.
    labels: nombres de categoría
    values: totales por categoría
    """
    data = fetch_categoria_counts()
    labels = [d["nombre_categoria"] for d in data]
    values = [d["total_productos"] for d in data]
    return labels, values

def data_for_chart_with_ids() -> Dict[str, List]:
    """
    Variante que además incluye los IDs (útil para drilldowns o tooltips).
    Retorna: {"ids": [...], "labels": [...], "values": [...]}
    """
    data = fetch_categoria_counts()
    return {
        "ids": [d["id_categoria"] for d in data],
        "labels": [d["nombre_categoria"] for d in data],
        "values": [d["total_productos"] for d in data],
    }

# Ejemplo rápido de uso (quitar en producción):
if __name__ == "__main__":
    labels, values = data_for_chart()
    print("Labels:", labels)
    print("Values:", values)