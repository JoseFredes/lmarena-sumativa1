# F3 · Núcleo algorítmico, eficiencia y POO

Fase 3: construir el núcleo algorítmico del proyecto (clases, recursión, mediciones de eficiencia) sobre el dataset de la Fase 2.

| Notebook | Qué hace |
|---|---|
| `F3_02_eficiencia.ipynb` | Compara varias implementaciones de tres tareas del pipeline (aplanar `conv_metadata`, recorrer un diccionario anidado, sumar el formato por fila), mide tiempo y memoria con distintos tamaños y justifica cuál se elige. |

El código que usa vive en `src/arena/eficiencia.py` (implementaciones) y `src/arena/medicion.py` (mediciones), con pruebas en `tests/test_eficiencia.py`.

## Cómo ejecutarlo

Con el entorno listo y los datos descargados en `data/raw/` (`make install` y `make data`):

```bash
.venv/bin/python -m jupyter nbconvert --to notebook --execute --inplace F3/F3_02_eficiencia.ipynb
```

Tarda unos 3 minutos, porque mide con las 135.634 filas. Los tiempos dependen de la máquina; el notebook registra el entorno en la sección 0. Lo que debe repetirse en cualquier equipo es el orden entre las versiones y los exponentes de crecimiento.
