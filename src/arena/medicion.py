"""Medición de tiempo y memoria de una función.

Módulo del proyecto modelo MCDI500. El código es el mismo que se desarrolla paso a
paso en F3/S2_F3_NucleoAlgoritmico_Eficiencia_POO.ipynb

Se mantiene medir() y se agregan mejor_tiempo() y comparar()
"""

import time
import tracemalloc
import timeit
import pandas as pd


def medir(funcion, *args, **kwargs):
    """Ejecuta la función y devuelve resultado, segundos y memoria pico en MB.

    *args recoge los argumentos posicionales en una tupla y **kwargs los
    argumentos con nombre en un diccionario. El asterisco es lo que hace el
    trabajo; los nombres args y kwargs son solo convención.
    """
    tracemalloc.start()
    inicio = time.perf_counter()
    resultado = funcion(*args, **kwargs)
    transcurrido = time.perf_counter() - inicio
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return resultado, transcurrido, pico / 1024 / 1024

def mejor_tiempo(funcion, *args, repeticiones=3, **kwargs):
    """Mide el tiempo de la función con timeit y devuelve el menor de varios intentos.

    Recibe: la función y cuántas veces repetir la medición.
    Devuelve: el menor tiempo.
    """
    tiempos = timeit.repeat(lambda: funcion(*args, **kwargs), number=1, repeat=repeticiones)
    return min(tiempos)

def comparar(implementaciones, *args, repeticiones=3, **kwargs):
    """Mide tiempo y memoria de varias veces con los mismos argumentos.

    Recibe: diccionario {nombre: funcion}, y cuantas veces repetir la comparación.
    Devuelve: segundos, peak de uso de memoria (MB) y cuántas veces es más lenta la lenta que la rápida
    """
    filas = []
    for nombre, funcion in implementaciones.items():
        # Tiempo sin tracemalloc; memoria en una ejecución aparte, con medir()
        segundos = mejor_tiempo(funcion, *args, repeticiones=repeticiones, **kwargs)
        _, _, memoria = medir(funcion, *args, **kwargs)
        filas.append({"implementacion": nombre, "segundos": segundos, "memoria_mb": memoria})
    tabla = pd.DataFrame(filas)
    tabla["veces_mas_lenta"] = tabla["segundos"] / tabla["segundos"].min()
    return tabla