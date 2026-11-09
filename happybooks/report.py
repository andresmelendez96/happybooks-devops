"""Genera una visualización y un informe HTML estático del catálogo."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import pandas as pd

from happybooks.analysis import calculate_metrics, format_cop, load_catalog


def create_price_chart(df: pd.DataFrame, output_path: Path) -> None:
    """Guarda un histograma de los precios actuales del catálogo."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    prices = df["precio_actual_cop"].astype(float)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(prices, bins=12, edgecolor="black")
    ax.set_title("Distribución de precios actuales – Happy Books")
    ax.set_xlabel("Precio actual (COP)")
    ax.set_ylabel("Cantidad de libros")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def build_html(df: pd.DataFrame, metrics: dict, chart_name: str) -> str:
    """Construye la página HTML con indicadores y los libros con mayor descuento."""
    discounted = df.dropna(subset=["descuento_calculado_pct"]).copy()
    discounted = discounted.sort_values(
        "descuento_calculado_pct", ascending=False
    ).head(10)

    rows = []
    for _, book in discounted.iterrows():
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(book['titulo']))}</td>"
            f"<td>{html.escape(str(book['autor']))}</td>"
            f"<td>{format_cop(float(book['precio_actual_cop']))}</td>"
            f"<td>{float(book['descuento_calculado_pct']):.1f}%</td>"
            "</tr>"
        )

    discount_average = (
        f"{metrics['descuento_promedio_pct']:.2f}%"
        if metrics["descuento_promedio_pct"] is not None
        else "No disponible"
    )

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Análisis del catálogo – Happy Books Colombia</title>
  <style>
    :root {{ color-scheme: light; font-family: Arial, sans-serif; }}
    body {{ margin: 0; background: #f4f7fb; color: #182433; }}
    header {{ background: #073b53; color: white; padding: 2rem max(5vw, 1rem); }}
    main {{ max-width: 1050px; margin: 2rem auto; padding: 0 1rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(190px,1fr)); gap: 1rem; }}
    .card, section {{ background: white; padding: 1.2rem; border-radius: 12px; box-shadow: 0 2px 10px #10203012; }}
    .value {{ font-size: 1.5rem; font-weight: 700; margin-top: .4rem; }}
    img {{ width: 100%; max-width: 850px; display: block; margin: 1rem auto; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ text-align: left; padding: .7rem; border-bottom: 1px solid #e5eaf0; }}
    th {{ background: #edf4f7; }}
    .note {{ color: #526273; font-size: .92rem; }}
    footer {{ padding: 2rem; text-align: center; color: #526273; }}
  </style>
</head>
<body>
<header>
  <h1>Análisis del catálogo de Happy Books Colombia</h1>
  <p>Proyecto académico de análisis de datos y flujo de trabajo DevOps.</p>
</header>
<main>
  <section>
    <h2>Resumen del conjunto de datos</h2>
    <div class="cards">
      <div class="card"><div>Libros analizados</div><div class="value">{metrics['total_libros']}</div></div>
      <div class="card"><div>Precio promedio</div><div class="value">{format_cop(metrics['precio_promedio_cop'])}</div></div>
      <div class="card"><div>Precio mediano</div><div class="value">{format_cop(metrics['precio_mediano_cop'])}</div></div>
      <div class="card"><div>Descuento promedio calculable</div><div class="value">{discount_average}</div></div>
    </div>
    <p class="note">El descuento promedio considera únicamente {metrics['libros_con_descuento_calculable']} libros con precio original disponible. Los valores corresponden al momento de la recolección y pueden cambiar en la tienda.</p>
  </section>
  <section style="margin-top:1rem">
    <h2>Distribución de precios actuales</h2>
    <img src="{html.escape(chart_name)}" alt="Histograma de precios actuales de los libros">
    <p class="note">Precio mínimo: {format_cop(metrics['precio_minimo_cop'])} · Precio máximo: {format_cop(metrics['precio_maximo_cop'])}.</p>
  </section>
  <section style="margin-top:1rem">
    <h2>Libros con mayores descuentos calculados</h2>
    <table>
      <thead><tr><th>Libro</th><th>Autor</th><th>Precio actual</th><th>Descuento</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </section>
  <section style="margin-top:1rem">
    <h2>Calidad de los datos</h2>
    <p>URL únicas: {metrics['urls_unicas']} de {metrics['total_libros']} registros.</p>
    <p>Precios actuales válidos: {metrics['precios_actuales_validos']}.</p>
    <p>Registros sin precio original: {metrics['precios_originales_faltantes']}.</p>
    <p class="note">Los precios originales ausentes se conservan como datos faltantes; no se interpretan como cero.</p>
  </section>
</main>
<footer>Proyecto académico – Happy Books Colombia</footer>
</body>
</html>
"""


def generate_report(csv_path: Path, output_dir: Path) -> dict:
    """Genera docs/index.html y docs/precios.png; devuelve las métricas."""
    df = load_catalog(csv_path)
    metrics = calculate_metrics(df)
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_path = output_dir / "precios.png"
    create_price_chart(df, chart_path)
    page = build_html(df, metrics, chart_path.name)
    (output_dir / "index.html").write_text(page, encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/catalogo_happy_books.csv"))
    parser.add_argument("--output", type=Path, default=Path("docs"))
    args = parser.parse_args()

    metrics = generate_report(args.input, args.output)
    print("Informe generado correctamente.")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
