# Notebook de la Evidencia de Aprendizaje 1

Se conserva aquí el cuaderno original de Google Colab de la Evidencia 1 (`Analizando_EA1_Happy_Books.ipynb`).

El cuaderno documenta el proceso exploratorio realizado con Happy Books Colombia:

- Inspección de la página y extracción del catálogo con Requests y BeautifulSoup.
- Limpieza, validación y análisis de precios con Pandas.
- Visualización de la distribución de precios con Matplotlib.
- Prueba de navegación automatizada con Selenium.
- Implementación de un spider con Scrapy y revisión de resultados, incluidos los registros incompletos y las respuestas HTTP 429.

El CSV consolidado que utiliza el proyecto DevOps se conserva por separado en `data/catalogo_happy_books.csv` para que el análisis y las pruebas automatizadas sean reproducibles sin depender de nuevas solicitudes al sitio web.
