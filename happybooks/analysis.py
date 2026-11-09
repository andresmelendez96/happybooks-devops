"""Carga, valida y analiza el catálogo de Happy Books Colombia."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = {
    "titulo",
    "autor",
    "precio_original_cop",
    "precio_actual_cop",
    "descuento",
    "url",
}


def load_catalog(csv_path: str | Path) -> pd.DataFrame:
    """Carga el CSV, valida su estructura y normaliza las columnas principales.

    Los precios originales ausentes se conservan como NaN; no se reemplazan por 0.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de datos: {path}")

    df = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Faltan columnas obligatorias en el CSV: {missing}")
    if df.empty:
        raise ValueError("El archivo CSV no contiene registros.")

    for column in ("titulo", "autor", "url"):
        df[column] = df[column].fillna("").astype(str).str.strip()

    df["precio_actual_cop"] = pd.to_numeric(
        df["precio_actual_cop"], errors="coerce"
    )
    df["precio_original_cop"] = pd.to_numeric(
        df["precio_original_cop"], errors="coerce"
    )

    if df["precio_actual_cop"].isna().any():
        raise ValueError("Hay libros sin un precio actual numérico válido.")
    if (df["precio_actual_cop"] < 0).any():
        raise ValueError("Se encontraron precios actuales negativos.")

    # Se recalcula el descuento a partir de los precios para evitar depender
    # de un texto promocional o de una columna calculada previamente.
    precio_original = df["precio_original_cop"]
    precio_actual = df["precio_actual_cop"]
    puede_calcular = precio_original.notna() & (precio_original > 0)
    df["descuento_calculado_pct"] = pd.NA
    df.loc[puede_calcular, "descuento_calculado_pct"] = (
        (precio_original[puede_calcular] - precio_actual[puede_calcular])
        / precio_original[puede_calcular]
        * 100
    )

    return df


def calculate_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """Calcula indicadores descriptivos del precio y los descuentos."""
    if df.empty:
        raise ValueError("No es posible calcular métricas con un catálogo vacío.")

    prices = pd.to_numeric(df["precio_actual_cop"], errors="coerce").dropna()
    discounts = pd.to_numeric(
        df["descuento_calculado_pct"], errors="coerce"
    ).dropna()

    if prices.empty:
        raise ValueError("No hay precios actuales válidos para analizar.")

    return {
        "total_libros": int(len(df)),
        "urls_unicas": int(df["url"].nunique()),
        "precios_actuales_validos": int(prices.count()),
        "precios_originales_disponibles": int(
            df["precio_original_cop"].notna().sum()
        ),
        "precio_minimo_cop": float(prices.min()),
        "precio_maximo_cop": float(prices.max()),
        "precio_promedio_cop": float(prices.mean()),
        "precio_mediano_cop": float(prices.median()),
        "descuento_promedio_pct": (
            float(discounts.mean()) if not discounts.empty else None
        ),
        "libros_con_descuento_calculable": int(discounts.count()),
        "precios_originales_faltantes": int(
            df["precio_original_cop"].isna().sum()
        ),
    }


def format_cop(value: float) -> str:
    """Formatea un valor numérico como pesos colombianos sin decimales."""
    return f"${value:,.0f}".replace(",", ".") + " COP"
