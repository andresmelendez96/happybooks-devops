from pathlib import Path

import pandas as pd
import pytest

from happybooks.analysis import (
    calculate_metrics,
    classify_price_ranges,
    load_catalog,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "catalogo_happy_books.csv"


def test_catalogo_original_se_carga_y_conserva_registros():
    df = load_catalog(DATA_FILE)

    assert len(df) == 142
    assert df["url"].nunique() == 142
    assert df["precio_actual_cop"].notna().all()
    assert df["precio_original_cop"].isna().sum() == 75


def test_metricas_principales_del_catalogo():
    df = load_catalog(DATA_FILE)
    metrics = calculate_metrics(df)

    assert metrics["total_libros"] == 142
    assert metrics["urls_unicas"] == 142
    assert metrics["precio_minimo_cop"] == 9900
    assert metrics["precio_maximo_cop"] == 202800
    assert metrics["precio_mediano_cop"] == 62150
    assert metrics["libros_con_descuento_calculable"] == 67
    assert metrics["descuento_promedio_pct"] == pytest.approx(27.8358208955)


def test_no_convierte_precio_original_ausente_en_cero(tmp_path):
    sample = pd.DataFrame(
        {
            "titulo": ["Libro de prueba"],
            "autor": ["Autor de prueba"],
            "precio_original_cop": [None],
            "precio_actual_cop": [50000],
            "descuento": [None],
            "url": ["https://example.com/libro"],
        }
    )
    csv_path = tmp_path / "catalogo.csv"
    sample.to_csv(csv_path, index=False)

    df = load_catalog(csv_path)

    assert pd.isna(df.loc[0, "precio_original_cop"])
    assert pd.isna(df.loc[0, "descuento_calculado_pct"])


def test_archivo_inexistente_genera_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_catalog(tmp_path / "no_existe.csv")

def test_clasifica_correctamente_los_limites_de_precios():
    datos = pd.DataFrame({
        "precio_actual_cop": [
            29999, 30000, 59999,
            60000, 99999, 100000
        ]
    })

    resultado = classify_price_ranges(datos)

    categorias_esperadas = [
        "Economico",
        "Intermedio",
        "Intermedio",
        "Costoso",
        "Costoso",
        "Premium"
    ]

    assert resultado["categoria_precio"].tolist() == categorias_esperadas

    # Comprobar que el DataFrame original no fue modificado.
    assert "categoria_precio" not in datos.columns


def test_clasifica_todos_los_libros_del_catalogo():
    df = load_catalog(DATA_FILE)

    resultado = classify_price_ranges(df)

    assert len(resultado) == 142
    assert resultado["categoria_precio"].notna().all()

    cantidades = resultado["categoria_precio"].value_counts()

    assert cantidades.sum() == 142
