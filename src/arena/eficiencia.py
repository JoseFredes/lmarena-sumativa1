"""Implementaciones alternativas de tres tareas del pipeline, para compararlas en F3.

Cada tarea tiene varias versiones que producen el MISMO resultado y se distinguen solo
por cómo lo calculan (tiempo y memoria). El notebook F3/F3_02_eficiencia.ipynb las mide
con medicion.comparar() y justifica cuál se queda.

Tarea 1. Aplanar conv_metadata (una columna de diccionarios) en columnas planas.
    aplanar_iterrows, aplanar_comprension, aplanar_json_normalize
Tarea 2. Recorrer las hojas de un diccionario anidado.
    recorrer_recursivo (el de transformadores.py) y recorrer_iterativo (con pila propia)
Tarea 3. Puntaje de formato por fila (encabezados + listas + negritas).
    formato_bucle, formato_apply, formato_vectorizado
"""

import pandas as pd

from .transformadores import AplanadorConvMetadata, recorrer

_NOMBRE = AplanadorConvMetadata().nombre_columna


# ── Tarea 1: aplanar conv_metadata ─────────────────────────────────────

def aplanar_iterrows(df):
    """Recorre el DataFrame fila a fila con iterrows() y arma un diccionario por fila.

    Recibe: DataFrame con la columna conv_metadata. Devuelve: DataFrame plano.
    Cada iteración construye una Series completa de la fila, aunque solo se use una celda.
    """
    filas = []
    for _, fila in df.iterrows():
        filas.append({_NOMBRE(ruta): hoja for ruta, hoja in recorrer(fila["conv_metadata"])})
    return pd.DataFrame(filas)


def aplanar_comprension(df):
    """Recorre solo la columna con una comprensión de listas (lo que hace AplanadorAnidado)."""
    filas = [
        {_NOMBRE(ruta): hoja for ruta, hoja in recorrer(anidado)}
        for anidado in df["conv_metadata"]
    ]
    return pd.DataFrame(filas)


def aplanar_json_normalize(df):
    """Usa pd.json_normalize, que aplana en una sola llamada; luego renombra como F2."""
    separador = "\x1f"       # carácter que no aparece en las claves, para separar los niveles
    plano = pd.json_normalize(df["conv_metadata"].tolist(), sep=separador)
    plano.columns = [_NOMBRE(tuple(c.split(separador))) for c in plano.columns]
    return plano


# ── Tarea 2: recorrer las hojas de un diccionario anidado ──────────────

def recorrer_recursivo(valor):
    """Devuelve la lista de (ruta, hoja) con la versión recursiva de transformadores.py."""
    return list(recorrer(valor))


def recorrer_iterativo(valor):
    """Misma salida con una pila explícita en vez de llamadas recursivas.

    Las hijas se apilan al revés para que salgan en el mismo orden que la versión recursiva.
    """
    hojas = []
    pila = [((), valor)]
    while pila:
        ruta, actual = pila.pop()
        if isinstance(actual, dict):
            for clave, interior in reversed(list(actual.items())):
                pila.append((ruta + (str(clave),), interior))
        else:
            hojas.append((ruta, actual))
    return hojas


def anidar(profundidad, hojas_por_nivel=2):
    """Construye un diccionario anidado de la profundidad pedida, para probar los recorridos."""
    interior = {f"hoja{i}": i for i in range(hojas_por_nivel)}
    for nivel in range(profundidad):
        interior = {"hijo": interior, "valor": nivel}
    return interior


# ── Tarea 3: puntaje de formato por fila ───────────────────────────────

def columnas_formato(df, lado="a"):
    """Columnas header_/list_/bold_ de un lado, ya aplanadas (header_a_h1, list_a_ordered...)."""
    return [c for c in df.columns if c.startswith((f"header_{lado}_", f"list_{lado}_", f"bold_{lado}_"))]


def formato_bucle(df, columnas):
    """Suma a mano con dos bucles de Python: fila por fila y columna por columna."""
    valores = df[columnas].values.tolist()
    resultado = []
    for fila in valores:
        total = 0
        for v in fila:
            total += v
        resultado.append(total)
    return pd.Series(resultado, index=df.index)


def formato_apply(df, columnas):
    """Usa DataFrame.apply(axis=1): una llamada de Python por fila."""
    return df[columnas].apply(lambda fila: fila.sum(), axis=1)


def formato_vectorizado(df, columnas):
    """Usa .sum(axis=1): la suma corre en código compilado, sin bucle de Python (como F2)."""
    return df[columnas].sum(axis=1)


# ── Medición por tamaño y exponente empírico ───────────────────────────

def medir_por_tamano(implementaciones, datos, tamanos, *args, armar=None, repeticiones=3):
    """Repite medicion.comparar() para varios tamaños de entrada.

    Recibe: diccionario {nombre: funcion}, los datos, la lista de tamaños y los argumentos
    extra que necesiten las funciones. ``armar(datos, n)`` decide cómo se obtiene la entrada
    de tamaño n (por defecto, las primeras n filas de un DataFrame).
    Devuelve: una tabla larga con las columnas de comparar() más ``n``.
    """
    from .medicion import comparar

    armar = armar or (lambda d, n: d.head(n))
    tablas = []
    for n in tamanos:
        entrada = armar(datos, n)
        tabla = comparar(implementaciones, entrada, *args, repeticiones=repeticiones)
        tabla["n"] = n
        tablas.append(tabla)
    return pd.concat(tablas, ignore_index=True)


def exponente(tabla):
    """Estima el exponente k de tiempo ≈ c·n^k y de memoria ≈ c·n^k, por implementación.

    Ajusta una recta a log(valor) contra log(n). Un exponente cercano a 1 indica un
    crecimiento lineal; cercano a 2, cuadrático. Es una estimación sobre los tamaños
    medidos, no una demostración.
    """
    import numpy as np

    filas = []
    for nombre, g in tabla.groupby("implementacion", sort=False):
        log_n = np.log(g["n"].astype(float))
        filas.append({
            "implementacion": nombre,
            "exponente_tiempo": np.polyfit(log_n, np.log(g["segundos"]), 1)[0],
            "exponente_memoria": np.polyfit(log_n, np.log(g["memoria_mb"]), 1)[0],
        })
    return pd.DataFrame(filas).set_index("implementacion").round(2)


def aplanar_json_con_esquema(df, columnas):
    """json_normalize y luego reindex al esquema aprendido, como hace AplanadorAnidado.

    Recibe: el DataFrame y la lista de columnas de salida (las de ``parametros["columnas"]``).
    Devuelve: un DataFrame con exactamente esas columnas, en ese orden; las que falten en el
    dato quedan como NaN. Junta la velocidad de json_normalize con el contrato del Transformador.
    """
    return aplanar_json_normalize(df).reindex(columns=columnas)
