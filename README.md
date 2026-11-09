# Happy Books – Análisis de catálogo con flujo DevOps

Proyecto académico de continuación de la Evidencia de Aprendizaje 1 de Programación para Análisis de Datos. Se utiliza el catálogo recopilado de Happy Books Colombia para procesar precios, calcular indicadores y generar un informe web estático.

## Objetivo

Aplicar control de versiones con Git y GitHub e implementar un flujo CI/CD con GitHub Actions para validar el código, ejecutar pruebas automatizadas y publicar el informe mediante GitHub Pages.

## Datos de entrada

El archivo `data/catalogo_happy_books.csv` contiene 142 productos recolectados en la Evidencia 1. Los precios originales ausentes se conservan como valores faltantes y no se sustituyen por cero.

Indicadores de referencia del CSV incluido:

| Indicador | Resultado |
|---|---:|
| Libros | 142 |
| URL únicas | 142 |
| Precio mínimo actual | $9.900 COP |
| Precio máximo actual | $202.800 COP |
| Precio promedio actual | $71.276 COP |
| Precio mediano actual | $62.150 COP |
| Libros con precio original disponible | 67 |
| Descuento promedio calculable | 27,84 % |

El descuento promedio se calcula únicamente sobre los libros con precio original disponible. Los valores son una fotografía del catálogo en el momento de la recolección y pueden cambiar.

## Estructura del proyecto

```text
happybooks-devops/
├── .github/workflows/ci-cd.yml
├── data/catalogo_happy_books.csv
├── docs/                     # Informe estático y gráfico generado
├── happybooks/
│   ├── __init__.py
│   ├── analysis.py            # Carga, validación y métricas
│   └── report.py              # Gráfico e informe HTML
├── notebooks/                 # Material complementario de Colab
├── tests/test_analysis.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.10 o superior.
- Git.
- Cuenta de GitHub.

## Ejecución local

En Windows PowerShell, desde la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m happybooks.report --input data/catalogo_happy_books.csv --output docs
```

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m happybooks.report --input data/catalogo_happy_books.csv --output docs
```

Al finalizar se generan `docs/index.html` y `docs/precios.png`. Abre `docs/index.html` en un navegador para consultar el informe.

## Pruebas y calidad

Ejecuta las pruebas unitarias con:

```bash
pytest -v
```

Verifica el estilo del código con:

```bash
ruff check happybooks tests
```

## Flujo de trabajo Git propuesto

1. Mantener `main` como rama estable.
2. Crear `feature/analisis-precios` para el procesamiento del catálogo.
3. Crear `feature/reporte-visualizaciones` para la página y sus gráficos. Esta segunda rama puede representar una colaboración simulada, documentando que el trabajo es individual.
4. Subir ramas y abrir Pull Requests hacia `main`.
5. Revisar, aprobar y fusionar los cambios.
6. Para demostrar rollback sin reescribir el historial remoto, utilizar `git revert <id-del-commit>` sobre un commit de prueba y documentar el resultado.

## Pipeline CI/CD

El flujo de GitHub Actions definido en `.github/workflows/ci-cd.yml` se activa al hacer `push` a `main`, al abrir o actualizar un Pull Request hacia `main`, o manualmente. Ejecuta estas etapas:

1. Instala dependencias.
2. Verifica estilo con Ruff.
3. Ejecuta pruebas unitarias con pytest.
4. Genera el informe y la visualización.
5. En cambios que llegan a `main`, prepara y publica `docs/` en GitHub Pages.

Para activar la publicación, configura GitHub Pages en el repositorio con la opción **GitHub Actions** como fuente de despliegue. La primera publicación debe verificarse desde la pestaña **Actions** y la configuración de **Pages**.

## Alcance y limitaciones

El análisis automatizado trabaja con el CSV ya recolectado en la Evidencia 1. No vuelve a consultar el sitio de Happy Books durante cada ejecución del pipeline, por lo que las pruebas son reproducibles y no dependen de límites de solicitudes del sitio. La página publicada presenta resultados derivados de la fecha de recolección del conjunto de datos, no precios en tiempo real.
