"""Carga y verificación del conjunto de datos de LMArena.

Se adapta modulo de carga.py. Se mantiene leer_archivo, verificar_esquema y cargar.
Se agrega asegurar_archivos y cargar_lmarena, que dejan disponiblos los 7 parquet del dataset y los cargan.
El código es el mismo que se desarrolla paso a paso en F3/S2_F3_NucleoAlgoritmico_Eficiencia_POO.ipynb; el cuaderno verifica que ambas
versiones producen el mismo resultado.
"""

import os

import pandas as pd
from huggingface_hub import hf_hub_download

from .io import RAW_DIR, REPO_ID

# Las 11 columnas de la data raw, en el orden del archivo.
# Las 3 columnas de prompts no se cargan por privacidad.

COLUMNAS_ESPERADAS = (
    "id", "model_a", "model_b", "winner", "evaluation_session_id", "evaluation_order", "conv_metadata", "category_tag", "language", "is_code", "timestamp",
)

# Los 7 archivos parquet con ruta relativa de Hugging Face
ARCHIVOS_PARQUET = [f"data/train-{i:05d}-of-00007.parquet" for i in range(7)]

def leer_archivo(ruta, columnas=None):
    """Lee el archivo según su extensión y devuelve un DataFrame.
 
    Recibe: ruta del archivo y, solo para parquet, la lista de columnas a leer
    (None lee todas). Devuelve: DataFrame de pandas.
    """
    extension = os.path.splitext(ruta)[1].lower()
 
    if extension in (".csv", ".txt"):
        return pd.read_csv(ruta, sep=None, engine="python", encoding="utf-8")
    if extension in (".xlsx", ".xls"):
        return pd.read_excel(ruta)
    if extension == ".parquet":
        # Lee solo las columnas necesarias evita cargar el texto de las conversaciones
        return pd.read_parquet(ruta, columns=columnas)
 
    raise ValueError(
        f"Extensión no reconocida: '{extension}'. "
        "Se admiten .csv, .txt, .xlsx, .xls y .parquet."
    )


def verificar_esquema(df, columnas_esperadas):
    """Comprueba que estén todas las columnas esperadas.
 
    Recibe: el DataFrame y la lista de columnas esperadas.
    Devuelve: un diccionario con cuántas se declararon, cuántas trae el archivo
    y cuáles sobran. Arroja KeyError si falta alguna.
    """
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        raise KeyError(
            f"Faltan columnas esperadas: {faltantes}\n"
            f"Columnas disponibles en el archivo: {list(df.columns)}"
        )
    sobrantes = [c for c in df.columns if c not in columnas_esperadas]
    return {"declaradas": len(columnas_esperadas),
            "en_archivo": df.shape[1],
            "no_declaradas": sobrantes}


def cargar(ruta, columnas_esperadas, columnas_numericas=()):
    """Carga un archivo y verifica su esquema.
 
    Recibe: ruta del archivo, columnas esperadas y columnas que deben ser numéricas.
    Devuelve: DataFrame cargado. Si el archivo no existe, se detiene con un error.
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    df = leer_archivo(ruta)
    # Las columnas numéricas se fuerzan a número: un texto suelto las
    # convertiría en columna de texto sin ningún aviso
    for columna in columnas_numericas:
        if columna in df.columns:
            df[columna] = pd.to_numeric(df[columna], errors="coerce")
    verificar_esquema(df, columnas_esperadas)
    return df

def asegurar_archivos(directorio=RAW_DIR):
    """Deja disponibles los 7 archivos parquet: usa los locales y descarga los que falten.
 
    Recibe: la carpeta de datos crudos (por defecto data/raw).
    Devuelve: la lista de rutas locales de los 7 archivos, en orden.
    """
    rutas = []
    for nombre_archivo in ARCHIVOS_PARQUET:
        ruta = directorio / nombre_archivo
        # Si el archivo ya está en data/raw se usa; si no, se descarga desde Hugging Face
        if not ruta.exists():
            hf_hub_download(
                repo_id=REPO_ID,
                filename=nombre_archivo,
                repo_type="dataset",
                local_dir=directorio,
            )
        rutas.append(ruta)
    return rutas

def cargar_lmarena(directorio=RAW_DIR):
    """Carga el dataset completo de LMArena (135.634 votos) y verifica su esquema.
 
    Recibe: la carpeta de datos crudos (por defecto data/raw).
    Devuelve: un DataFrame con las 11 columnas de COLUMNAS_ESPERADAS; conv_metadata
    y category_tag quedan como diccionarios anidados, igual que en load_raw de F2.
    """
    rutas = asegurar_archivos(directorio)
    # Se leen los 7 archivos con las mismas columnas y se unen en un solo DataFrame
    partes = [leer_archivo(str(ruta), columnas=list(COLUMNAS_ESPERADAS)) for ruta in rutas]
    df = pd.concat(partes, ignore_index=True)
    verificar_esquema(df, COLUMNAS_ESPERADAS)
    return df