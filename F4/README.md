# F4 · Análisis y comunicación de resultados

`F4_01_analisis_integrador.ipynb` recorre el proyecto en orden y responde la pregunta P1: ¿gana más seguido la respuesta más larga o con más formato?

1. Registra el entorno (F1).
2. Carga el dato crudo, lo pasa por `pasos_f3()` y lo valida (F2 y F3).
3. Calcula tasas de victoria, regresiones logísticas y un control por modelo (F4).
4. Guarda tres figuras en `report/figures/` (`f4_*.png`).

El código del análisis está en `src/arena/analisis.py` y los gráficos en `src/arena/plots.py`; tienen pruebas en `tests/test_analisis.py` y `tests/test_plots.py`.

Para ejecutarlo, desde la raíz y con los datos descargados (`make data`):

```bash
.venv/bin/python -m jupyter nbconvert --to notebook --execute --inplace F4/F4_01_analisis_integrador.ipynb
```

Tarda unos 15 segundos.
