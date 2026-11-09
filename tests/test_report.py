from pathlib import Path

from happybooks.report import generate_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "catalogo_happy_books.csv"


def test_informe_genera_html_y_graficas_con_clasificacion(tmp_path):
    metrics = generate_report(DATA_FILE, tmp_path)

    html_file = tmp_path / "index.html"
    price_chart = tmp_path / "precios.png"
    category_chart = tmp_path / "categorias_precios.png"

    assert html_file.exists()
    assert price_chart.exists()
    assert category_chart.exists()

    html_content = html_file.read_text(encoding="utf-8")

    assert "Clasificación de libros por rango de precios" in html_content
    assert "Económico" in html_content
    assert "Intermedio" in html_content
    assert "Costoso" in html_content
    assert "Premium" in html_content

    assert metrics["total_libros"] == 142
    assert sum(metrics["libros_por_categoria"].values()) == 142