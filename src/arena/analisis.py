"""Análisis de la pregunta P1: ¿gana más seguido la respuesta más larga o con más formato?

Todas las funciones reciben el dataset limpio (`arena_clean.parquet`, salida de `pasos_f3()`)
y devuelven tablas pequeñas. Solo usan NumPy y pandas: la regresión logística se resuelve con
mínimos cuadrados ponderados iterados (IRLS), así no hace falta agregar dependencias.

Solo se habla de asociaciones: el estudio es observacional.
"""
import numpy as np
import pandas as pd

Z95 = 1.959964  # cuantil 97,5 % de la normal estándar


def votos_decisivos(df: pd.DataFrame) -> pd.DataFrame:
    """Deja los votos con ganador (A o B) y agrega las variables para comparar.

    Recibe: el dataset limpio. Devuelve: una copia solo con `winner_binary` en {"a", "b"} y tres
    columnas nuevas: `y` (1 si ganó A), `dif_tokens_log` (tokens_log_a - tokens_log_b) y
    `dif_formato_log` (log1p(format_a) - log1p(format_b)). Las diferencias son positivas cuando
    A es más larga o tiene más formato. El logaritmo del formato evita que unas pocas respuestas
    con cientos de marcas dominen la diferencia.
    """
    faltan = {"winner_binary", "tokens_log_a", "tokens_log_b", "format_a", "format_b"} - set(df.columns)
    if faltan:
        raise KeyError(f"faltan columnas del dataset limpio: {sorted(faltan)}")
    d = df[df["winner_binary"].isin(["a", "b"])].copy()
    d["y"] = (d["winner_binary"] == "a").astype(int)
    d["dif_tokens_log"] = d["tokens_log_a"].astype(float) - d["tokens_log_b"].astype(float)
    d["dif_formato_log"] = np.log1p(d["format_a"]) - np.log1p(d["format_b"])
    return d


def intervalo_wilson(exitos, n, z: float = Z95):
    """Intervalo de confianza de Wilson para una proporción (acepta números o arreglos).

    Funciona mejor que el intervalo normal cuando la proporción está cerca de 0 o de 1 o n es
    chico. Con n = 0 devuelve (nan, nan).
    """
    exitos = np.asarray(exitos, dtype=float)
    n = np.asarray(n, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = exitos / n
        centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
        mitad = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    bajo, alto = centro - mitad, centro + mitad
    if bajo.ndim == 0:
        return float(bajo), float(alto)
    return bajo, alto


def gana_el_mayor(d: pd.DataFrame, columna: str) -> dict:
    """Proporción de votos en que gana el lado que tiene "más" según `columna`.

    `columna` es `longer_response` o `more_formatted` (valores "a", "b" o "equal"). Los casos
    "equal" no aportan información y se excluyen. Devuelve n, victorias, tasa e IC 95 %.
    """
    if columna not in d.columns:
        raise KeyError(columna)
    x = d[d[columna] != "equal"]
    exitos = int((x[columna] == x["winner_binary"]).sum())
    n = len(x)
    bajo, alto = intervalo_wilson(exitos, n)
    return {"n": n, "victorias": exitos, "tasa": exitos / n if n else float("nan"), "ic_bajo": bajo, "ic_alto": alto}


def tasa_por_tramos(d: pd.DataFrame, columna: str, tramos=10, y: str = "y") -> pd.DataFrame:
    """Tasa de victoria de A por tramos de `columna`, con IC 95 % de Wilson.

    `tramos` es un entero (cuantiles de igual tamaño) o una lista de cortes. Devuelve una fila por
    tramo con el centro (mediana de `columna` en el tramo), n, tasa e intervalo.
    """
    if isinstance(tramos, int):
        grupo = pd.qcut(d[columna], tramos, duplicates="drop")
    else:
        grupo = pd.cut(d[columna], tramos)
    g = d.groupby(grupo, observed=True)
    tabla = pd.DataFrame({"centro": g[columna].median(), "n": g.size(), "victorias": g[y].sum()})
    tabla["tasa"] = tabla["victorias"] / tabla["n"]
    tabla["ic_bajo"], tabla["ic_alto"] = intervalo_wilson(tabla["victorias"], tabla["n"])
    tabla.index = tabla.index.astype(str)
    return tabla


def tasa_empates_por_diferencia(df: pd.DataFrame, tramos=(0, 0.1, 0.25, 0.5, 1, 2, 10)) -> pd.DataFrame:
    """Proporción de votos sin ganador (`tie` o `both_bad`) según cuánto difiere el largo.

    Usa |tokens_log_a - tokens_log_b|. Sirve para ver si los empates se concentran cuando las
    dos respuestas tienen un largo parecido.
    """
    dif = (df["tokens_log_a"].astype(float) - df["tokens_log_b"].astype(float)).abs()
    sin_ganador = (df["winner_binary"] == "other").astype(int)
    grupo = pd.cut(dif, list(tramos), include_lowest=True)
    g = sin_ganador.groupby(grupo, observed=True)
    tabla = pd.DataFrame({"n": g.size(), "sin_ganador": g.sum()})
    tabla["tasa"] = tabla["sin_ganador"] / tabla["n"]
    tabla["ic_bajo"], tabla["ic_alto"] = intervalo_wilson(tabla["sin_ganador"], tabla["n"])
    tabla.index = tabla.index.astype(str)
    return tabla


def regresion_logistica(X, y, nombres=None, iteraciones: int = 50, tolerancia: float = 1e-9) -> pd.DataFrame:
    """Regresión logística por IRLS (Newton-Raphson), con intercepto.

    Recibe: X (n x k, sin la columna de unos), y (0/1) y los nombres de las columnas.
    Devuelve: una tabla con coeficiente, error estándar, z, p aproximado (normal), IC 95 % y
    razón de odds. Lanza ValueError si hay datos faltantes, si y no es 0/1 o si la matriz es
    singular (por ejemplo, dos columnas idénticas) o no converge.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    if len(X) != len(y):
        raise ValueError("X e y tienen distinto número de filas")
    if np.isnan(X).any() or np.isnan(y).any():
        raise ValueError("hay valores faltantes en X o en y")
    if not set(np.unique(y)) <= {0.0, 1.0}:
        raise ValueError("y debe contener solo 0 y 1")
    nombres = list(nombres) if nombres is not None else [f"x{i + 1}" for i in range(X.shape[1])]
    if len(nombres) != X.shape[1]:
        raise ValueError("la cantidad de nombres no coincide con las columnas de X")
    A = np.column_stack([np.ones(len(X)), X])
    b = np.zeros(A.shape[1])
    for _ in range(iteraciones):
        p = 1 / (1 + np.exp(-(A @ b)))
        w = p * (1 - p)
        H = A.T @ (A * w[:, None])
        try:
            paso = np.linalg.solve(H, A.T @ (y - p))
        except np.linalg.LinAlgError as e:
            raise ValueError("matriz singular: hay columnas repetidas o constantes") from e
        b = b + paso
        if np.max(np.abs(paso)) < tolerancia:
            break
    else:
        raise ValueError("la regresión no convergió")
    se = np.sqrt(np.diag(np.linalg.inv(H)))
    z = b / se
    p_valor = 2 * (1 - 0.5 * (1 + _erf(np.abs(z) / np.sqrt(2))))
    tabla = pd.DataFrame(
        {"coef": b, "error_est": se, "z": z, "p": p_valor,
         "ic_bajo": b - Z95 * se, "ic_alto": b + Z95 * se, "odds": np.exp(b)},
        index=["intercepto", *nombres],
    )
    return tabla


def _erf(x):
    """Función de error (aproximación de Abramowitz y Stegun 7.1.26, error < 1,5e-7)."""
    x = np.asarray(x, dtype=float)
    t = 1 / (1 + 0.3275911 * x)
    poli = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return 1 - poli * np.exp(-x * x)


def estandarizar(d: pd.DataFrame, columnas) -> pd.DataFrame:
    """Devuelve las columnas centradas y divididas por su desviación estándar (copia).

    Sirve para comparar coeficientes de variables en escalas distintas. Una columna constante
    lanza ValueError, porque no se puede dividir por cero.
    """
    x = d[list(columnas)].astype(float)
    sd = x.std(ddof=0)
    if (sd == 0).any():
        raise ValueError(f"columna constante: {list(sd[sd == 0].index)}")
    return (x - x.mean()) / sd


def modelos_p1(d: pd.DataFrame) -> pd.DataFrame:
    """Ajusta tres regresiones y devuelve los coeficientes estandarizados de las diferencias.

    Los tres modelos explican `y` (gana A) con: solo longitud, solo formato y ambos. Sirve para
    ver cuánto del efecto del formato queda cuando se controla por longitud.
    """
    z = estandarizar(d, ["dif_tokens_log", "dif_formato_log"])
    filas = []
    for nombre, cols in [("solo longitud", ["dif_tokens_log"]),
                         ("solo formato", ["dif_formato_log"]),
                         ("longitud y formato", ["dif_tokens_log", "dif_formato_log"])]:
        t = regresion_logistica(z[cols], d["y"], cols)
        for var in cols:
            fila = t.loc[var].to_dict()
            fila.update(modelo=nombre, variable=var, n=len(d))
            filas.append(fila)
    return pd.DataFrame(filas).set_index(["modelo", "variable"])


def coeficientes_por_subconjunto(d: pd.DataFrame, subconjuntos: dict) -> pd.DataFrame:
    """Ajusta el modelo con longitud y formato en cada subconjunto de votos.

    `subconjuntos` mapea un nombre a una máscara booleana alineada con `d`. En cada uno las dos
    variables se estandarizan con su propia media y desviación, así los coeficientes se leen
    como "cambio en el log-odds de que gane A por cada desviación estándar de diferencia".
    Sirve para revisar si el resultado se sostiene fuera del conjunto completo.
    """
    filas = []
    for nombre, mascara in subconjuntos.items():
        sub = d[mascara]
        if len(sub) < 50:
            raise ValueError(f"el subconjunto '{nombre}' tiene solo {len(sub)} votos")
        t = modelos_p1(sub).xs("longitud y formato", level="modelo")
        for var, fila in t.iterrows():
            filas.append({"subconjunto": nombre, "variable": var, "n": len(sub),
                          "coef": fila["coef"], "ic_bajo": fila["ic_bajo"], "ic_alto": fila["ic_alto"]})
    return pd.DataFrame(filas).set_index(["subconjunto", "variable"])


def efecto_con_modelos(d: pd.DataFrame, minimo: int = 100) -> pd.DataFrame:
    """Efecto del largo y del formato sin y con control por el modelo de cada lado.

    Es un Bradley-Terry con control de estilo: además de las dos diferencias estandarizadas, el
    modelo incluye una columna por modelo de lenguaje (+1 si juega de A, -1 si juega de B, 0 si no
    participa). Así el efecto del largo se mide dentro de cada par de modelos, y un modelo que
    gana mucho y además escribe largo no se confunde con el efecto del largo. El modelo más
    frecuente queda como referencia. Los modelos con menos de `minimo` apariciones se dejan fuera
    junto con sus votos, porque con tan pocos datos su coeficiente no se puede estimar.

    Devuelve los coeficientes de las dos variables de estilo, ajustados sobre los mismos votos,
    sin y con las columnas de modelo. `d` necesita `model_a` y `model_b`.
    """
    faltan = {"model_a", "model_b"} - set(d.columns)
    if faltan:
        raise KeyError(f"faltan columnas: {sorted(faltan)}")
    cuenta = pd.concat([d["model_a"], d["model_b"]]).value_counts()
    validos = list(cuenta[cuenta >= minimo].index)
    if len(validos) < 2:
        raise ValueError("hace falta al menos dos modelos con suficientes votos")
    sub = d[d["model_a"].isin(validos) & d["model_b"].isin(validos)]
    referencia = cuenta.index[0]
    modelos = [m for m in validos if m != referencia]
    M = pd.DataFrame({m: (sub["model_a"] == m).astype(float) - (sub["model_b"] == m).astype(float) for m in modelos})
    estilo = ["dif_tokens_log", "dif_formato_log"]
    z = estandarizar(sub, estilo)

    sin = regresion_logistica(z, sub["y"], estilo)
    con = regresion_logistica(pd.concat([z, M], axis=1), sub["y"], estilo + modelos)
    filas = []
    for etiqueta, t in [("sin control de modelo", sin), ("con control de modelo", con)]:
        for var in estilo:
            r = t.loc[var]
            filas.append({"ajuste": etiqueta, "variable": var, "n": len(sub), "n_modelos": len(validos),
                          "coef": r["coef"], "ic_bajo": r["ic_bajo"], "ic_alto": r["ic_alto"], "odds": r["odds"]})
    return pd.DataFrame(filas).set_index(["ajuste", "variable"])
