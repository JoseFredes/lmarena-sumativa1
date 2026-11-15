"""Pruebas de las clases de transformadores.py: casos normales, límite y errores."""
import pandas as pd
import pytest

from arena.transformadores import (
    AplanadorAnidado,
    AplanadorCategoryTag,
    AplanadorConvMetadata,
    ConversorCategoria,
    ConversorTipo,
    DerivadorEstilo,
    EliminadorColumnas,
    Transformador,
    pasos_f3,
    recorrer,
)


# ── recorrer (recursión) ───────────────────────────────────────────────

def test_recorrer_hoja_simple():
    assert list(recorrer(5)) == [((), 5)]


def test_recorrer_diccionario_vacio_no_entrega_hojas():
    assert list(recorrer({})) == []


def test_recorrer_baja_varios_niveles():
    anidado = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    assert list(recorrer(anidado)) == [(("a",), 1), (("b", "c"), 2), (("b", "d", "e"), 3)]


# ── clase base ─────────────────────────────────────────────────────────

def test_base_exige_implementar_aprender_y_aplicar():
    paso = Transformador("x")
    df = pd.DataFrame({"x": [1]})
    with pytest.raises(NotImplementedError):
        paso.aprender(df)
    with pytest.raises(NotImplementedError):
        paso.aplicar(df)


def test_transformar_antes_de_ajustar_falla():
    paso = ConversorTipo("x", "float64")
    with pytest.raises(RuntimeError, match="ajustar antes de transformar"):
        paso.transformar(pd.DataFrame({"x": [1]}))


def test_ajustar_con_columna_ausente_falla():
    with pytest.raises(KeyError, match="no existe"):
        ConversorTipo("falta", "int16").ajustar(pd.DataFrame({"x": [1]}))


def test_ajustar_devuelve_el_propio_paso_y_permite_encadenar():
    paso = ConversorTipo("x", "float64")
    assert paso.ajustar(pd.DataFrame({"x": [1]})) is paso


def test_parametros_es_una_copia_defensiva():
    paso = ConversorTipo("x", "float64").ajustar(pd.DataFrame({"x": [1]}))
    paso.parametros["tipo_nuevo"] = "roto"
    assert paso.parametros["tipo_nuevo"] == "float64"


def test_transformar_no_modifica_el_dataframe_recibido():
    df = pd.DataFrame({"x": [1, 2]})
    ConversorTipo("x", "float64").ajustar_transformar(df)
    assert df["x"].dtype == "int64"


def test_nombre_incluye_clase_y_columna():
    assert ConversorTipo("is_code", "bool").nombre == "ConversorTipo(is_code)"


# ── aplanadores ────────────────────────────────────────────────────────

def test_aplanador_conv_metadata_nombres_como_f2(raw_anidado):
    plano = AplanadorConvMetadata().ajustar_transformar(raw_anidado)
    assert "conv_metadata" not in plano.columns
    assert {"header_a_h2", "list_a_unordered", "bold_a_asterisk", "bold_b_underscore"} <= set(plano.columns)
    assert len(plano) == len(raw_anidado)
    assert plano.loc[0, "bold_a_asterisk"] == 4


def test_aplanador_category_tag_nombres_como_f2(raw_anidado):
    plano = AplanadorCategoryTag().ajustar_transformar(raw_anidado)
    assert {"cat_creative_writing", "cat_creative_writing_score", "cat_criteria_complexity", "cat_math"} <= set(plano.columns)


def test_aplanador_conserva_esquema_si_al_conjunto_nuevo_le_falta_una_clave(raw_anidado):
    paso = AplanadorConvMetadata().ajustar(raw_anidado)
    incompleto = raw_anidado.copy()
    incompleto["conv_metadata"] = [{"sum_user_tokens": 7}] * 3
    plano = paso.transformar(incompleto)
    assert list(plano.columns[-1:]) == [paso.parametros["columnas"][-1]]
    assert plano["header_a_h2"].isna().all()       # la clave faltante queda como NaN


def test_aplanador_base_exige_nombre_columna():
    with pytest.raises(NotImplementedError):
        AplanadorAnidado("conv_metadata").nombre_columna(("a",))


# ── conversores ────────────────────────────────────────────────────────

def test_conversor_categoria_aprende_el_vocabulario():
    df = pd.DataFrame({"w": ["b", "a", "b"]})
    paso = ConversorCategoria("w").ajustar(df)
    assert paso.parametros["categorias"] == ["a", "b"]
    assert paso.transformar(df)["w"].dtype == "category"


def test_conversor_categoria_valor_nuevo_queda_como_faltante():
    paso = ConversorCategoria("w").ajustar(pd.DataFrame({"w": ["a", "b"]}))
    nuevo = paso.transformar(pd.DataFrame({"w": ["a", "z"]}))
    assert nuevo["w"].isna().tolist() == [False, True]


def test_conversor_tipo_registra_tipo_original_y_nuevo():
    paso = ConversorTipo("x", "int16").ajustar(pd.DataFrame({"x": [1, 2]}))
    assert paso.parametros == {"tipo_original": "int64", "tipo_nuevo": "int16"}
    assert paso.transformar(pd.DataFrame({"x": [1, 2]}))["x"].dtype == "int16"


def test_conversor_tipo_acepta_enteros_con_faltantes():
    df = pd.DataFrame({"x": [1.0, None, 3.0]})
    salida = ConversorTipo("x", "Int8").ajustar_transformar(df)
    assert str(salida["x"].dtype) == "Int8"
    assert salida["x"].isna().sum() == 1


def test_conversor_tipo_con_valor_imposible_falla():
    with pytest.raises(ValueError):
        ConversorTipo("x", "int16").ajustar_transformar(pd.DataFrame({"x": ["a"]}))


# ── derivador y eliminador ─────────────────────────────────────────────

def test_derivador_sin_columnas_markdown_pide_aplanar_antes(raw_anidado):
    with pytest.raises(KeyError, match="aplanar conv_metadata"):
        DerivadorEstilo().ajustar(raw_anidado)


def test_derivador_crea_las_siete_variables(raw_anidado):
    plano = AplanadorConvMetadata().ajustar_transformar(raw_anidado)
    plano = AplanadorCategoryTag().ajustar_transformar(plano)
    salida = DerivadorEstilo().ajustar_transformar(plano)
    nuevas = {"format_a", "format_b", "tokens_log_a", "tokens_log_b",
              "longer_response", "more_formatted", "winner_binary"}
    assert nuevas <= set(salida.columns)
    assert salida.loc[0, "format_a"] == 9       # 2 encabezados + 3 listas + 4 negritas


def test_eliminador_quita_la_columna():
    salida = EliminadorColumnas("y").ajustar_transformar(pd.DataFrame({"x": [1], "y": [2]}))
    assert list(salida.columns) == ["x"]


def test_eliminador_con_columna_ausente_no_falla_en_aplicar():
    # ajustar() exige que exista; si desaparece después, aplicar() la ignora
    paso = EliminadorColumnas("y").ajustar(pd.DataFrame({"x": [1], "y": [2]}))
    assert list(paso.transformar(pd.DataFrame({"x": [1]})).columns) == ["x"]


# ── pasos_f3 ───────────────────────────────────────────────────────────

def test_pasos_f3_son_nueve_transformadores():
    pasos = pasos_f3()
    assert len(pasos) == 9
    assert all(isinstance(p, Transformador) for p in pasos)
