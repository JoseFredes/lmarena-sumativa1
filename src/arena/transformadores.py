"""Transformadores: la clase base y sus clases hijas.

Se adapta el módulo transformadores.py La clase base Transformador se mantiene igual. 
Las clases hijas del modelo (imputar, codificar, escalar) se reemplazan por los pasos que necesita LMArena:
aplanar las columnas anidadas, convertir tipos y derivar las variables de estilo.
Juntos producen el mismo dataset que clean_dataset() de F2.
"""
import pandas as pd

from .preprocessing import derive_variables

# ---- 1. Clase base (igual a la del proyecto modelo) -----------------
class Transformador:
    """Clase base: lo que todos los pasos del pipeline comparten.

    No se usa directamente. Define el contrato (ajustar, transformar) y controla
    el estado; las clases hijas solo completan aprender() y aplicar().
    """

    def __init__(self, columna):
        # Columna sobre la que trabaja el paso (atributo público)
        self.columna = columna

        # Atributos internos (guion bajo): no se tocan desde fuera de la clase
        self._parametros = {}       # lo que el paso aprende del conjunto
        self._ajustado = False      # impide transformar antes de ajustar

    @property
    def nombre(self):
        # Nombre de la clase real del objeto y su columna, p. ej. ConversorTipo(is_code)
        return f"{type(self).__name__}({self.columna})"

    @property
    def parametros(self):
        # Copia defensiva: quien la recibe no puede cambiar el estado interno
        return dict(self._parametros)

    def ajustar(self, df):
        """Aprende los parámetros del conjunto que recibe y devuelve el propio paso."""
        # 1) Validar la entrada antes de trabajar
        if self.columna not in df.columns:
            raise KeyError(f"{self.nombre}: la columna no existe en el conjunto.")
        # 2) La clase hija decide qué se aprende
        self._parametros = self.aprender(df)
        # 3) Registrar que ya se ajustó
        self._ajustado = True
        # 4) Devolver self permite encadenar: paso.ajustar(df).transformar(df)
        return self

    def transformar(self, df):
        """Aplica la transformación con lo aprendido en ajustar(), sobre una copia de df."""
        if not self._ajustado:
            raise RuntimeError(f"{self.nombre}: hay que ajustar antes de transformar.")
        # df.copy(): el DataFrame recibido nunca se modifica
        return self.aplicar(df.copy())

    def ajustar_transformar(self, df):
        """Atajo: aprender y aplicar sobre el mismo conjunto."""
        return self.ajustar(df).transformar(df)

    # ---- Métodos que cada clase hija DEBE implementar -------------------

    def aprender(self, df):
        """Calcula y devuelve los parámetros. Lo implementa cada clase hija."""
        raise NotImplementedError("Cada clase hija debe implementar aprender().")

    def aplicar(self, df):
        """Aplica la transformación. Lo implementa cada clase hija."""
        raise NotImplementedError("Cada clase hija debe implementar aplicar().")


# ---- 2. Aplanamiento de columnas anidadas (recursivo) ---------------


def recorrer(valor, ruta=()):
    """Entrega (ruta, hoja) por cada hoja de un diccionario anidado, a cualquier profundidad.

    Recibe: un valor (diccionario o no) y la ruta recorrida hasta él.
    Devuelve: un generador de pares (tupla de claves, valor de la hoja).
    Caso base: el valor no es un diccionario, así que es una hoja.
    Caso recursivo: se baja un nivel por cada clave.
    """
    if not isinstance(valor, dict):          # caso base: una hoja
        yield ruta, valor
        return
    for clave, interior in valor.items():    # caso recursivo: un nivel más abajo
        yield from recorrer(interior, ruta + (str(clave),))


class AplanadorAnidado(Transformador):
    """Reemplaza una columna de diccionarios por una columna por cada hoja.

    aprender() guarda la lista de columnas de salida (el esquema), en orden de
    primera aparición; aplicar() devuelve siempre esa lista, aunque a un conjunto
    nuevo le falte alguna clave (queda como faltante). Las clases hijas solo
    definen nombre_columna(): cómo se nombra cada hoja.
    """

    def nombre_columna(self, ruta):
        """Convierte la ruta de una hoja en nombre de columna. Lo implementa cada hija."""
        raise NotImplementedError("Cada aplanador debe implementar nombre_columna().")

    def _filas_planas(self, serie):
        # Devuelve: una lista con un diccionario plano por fila {columna: valor}
        return [
            {self.nombre_columna(ruta): hoja for ruta, hoja in recorrer(anidado)}
            for anidado in serie
        ]

    def aprender(self, df):
        filas = self._filas_planas(df[self.columna])
        # dict.fromkeys conserva el orden de primera aparición y quita repetidos
        columnas = list(dict.fromkeys(clave for fila in filas for clave in fila))
        return {"columnas": columnas}

    def aplicar(self, df):
        filas = self._filas_planas(df[self.columna])
        planas = pd.DataFrame(filas, columns=self._parametros["columnas"])
        resto = df.drop(columns=[self.columna]).reset_index(drop=True)
        # Igual que F2: primero las demás columnas y al final las nuevas
        return pd.concat([resto, planas], axis=1)


class AplanadorConvMetadata(AplanadorAnidado):
    """Aplana conv_metadata: tokens y marcas Markdown de cada respuesta (26 columnas).

    header_count_a → h2 queda header_a_h2; las negritas ** y __ quedan
    asterisk y underscore, los mismos nombres de F2.
    """

    _NEGRITAS = {"**": "asterisk", "__": "underscore"}

    def __init__(self, columna="conv_metadata"):
        super().__init__(columna)

    def nombre_columna(self, ruta):
        if len(ruta) == 1:                                    # p. ej. sum_user_tokens
            return ruta[0]
        prefijo = ruta[0].replace("_count", "")              # header_count_a → header_a
        resto = [self._NEGRITAS.get(parte, parte) for parte in ruta[1:]]
        return "_".join([prefijo, *resto])


class AplanadorCategoryTag(AplanadorAnidado):
    """Aplana category_tag: etiquetas del clasificador de LMArena (12 columnas).

    criteria_v0.1 → complexity queda cat_criteria_complexity; si la clave
    interna repite el grupo (math_v0.1 → math) queda cat_math.
    """

    def __init__(self, columna="category_tag"):
        super().__init__(columna)

    def nombre_columna(self, ruta):
        if len(ruta) == 1:                                    # grupo sin subclaves (como F2)
            return f"cat_{ruta[0]}"
        grupo = ruta[0].rsplit("_v", 1)[0]                   
        resto = [parte for parte in ruta[1:] if parte != grupo]   
        return "_".join(["cat", grupo, *resto])


# ---- 3. Conversión de tipos ------------------------------------------


class ConversorCategoria(Transformador):
    """Convierte una columna de texto a categoría, con las categorías aprendidas.

    Como el CodificadorNominal del modelo, el vocabulario se aprende en el ajuste:
    un valor que solo aparece en prueba queda como faltante (NaN) en vez de crear
    una categoría que el ajuste nunca vio.
    """

    def aprender(self, df):
        # Las mismas categorías, en el mismo orden, que crearía astype("category")
        return {"categorias": list(df[self.columna].astype("category").cat.categories)}

    def aplicar(self, df):
        tipo = pd.CategoricalDtype(self._parametros["categorias"])
        df[self.columna] = df[self.columna].astype(tipo)
        return df


class ConversorTipo(Transformador):
    """Convierte una columna a un tipo fijo (por ejemplo bool o int16)."""

    def __init__(self, columna, tipo):
        super().__init__(columna)
        self.tipo = tipo            

    def aprender(self, df):
        # No hay nada que aprender del dato: se registra el tipo de origen y el de destino
        return {"tipo_original": str(df[self.columna].dtype), "tipo_nuevo": self.tipo}

    def aplicar(self, df):
        df[self.columna] = df[self.columna].astype(self.tipo)
        return df


# ---- Variables de estilo para P1 -------------------------------------


class DerivadorEstilo(Transformador):
    """Crea las 7 variables de estilo de F2 (format_a/b, tokens_log_a/b, ...).

    No reescribe el cálculo: llama a derive_variables() de F2, para que haya una
    sola versión del código. Aprende qué columnas Markdown suman format_a y format_b.
    """

    _PREFIJOS = ("header", "list", "bold")

    def __init__(self, columna="winner"):
        super().__init__(columna)

    def aprender(self, df):
        parametros = {}
        for lado in ("a", "b"):
            # Columnas Markdown del lado: header_a_*, list_a_*, bold_a_*
            marcas = [c for c in df.columns
                      if any(c.startswith(f"{p}_{lado}_") for p in self._PREFIJOS)]
            if not marcas:
                raise KeyError(f"{self.nombre}: no hay columnas Markdown del lado {lado}; "
                               "hay que aplanar conv_metadata antes.")
            parametros[f"columnas_format_{lado}"] = marcas
        return parametros

    def aplicar(self, df):
        return derive_variables(df)


def pasos_f2():
    """Los pasos del pipeline de F2, en el mismo orden que clean_dataset().

    Devuelve: una lista de transformadores listos para pasarle a Pipeline.
    """
    return [
        AplanadorConvMetadata(),
        AplanadorCategoryTag(),
        ConversorCategoria("winner"),
        ConversorCategoria("language"),
        ConversorTipo("is_code", "bool"),
        ConversorTipo("evaluation_order", "int16"),
        DerivadorEstilo(),
    ]
