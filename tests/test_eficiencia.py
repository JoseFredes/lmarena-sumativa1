"""Las implementaciones alternativas deben dar el mismo resultado; solo cambia el costo."""
import pandas as pd
import pytest

from arena.eficiencia import (
    anidar,
    aplanar_comprension,
    aplanar_iterrows,
    aplanar_json_con_esquema,
    aplanar_json_normalize,
    columnas_formato,
    exponente,
    formato_apply,
    formato_bucle,
    formato_vectorizado,
    medir_por_tamano,
    recorrer_iterativo,
    recorrer_recursivo,
)
from arena.transformadores import AplanadorConvMetadata


@pytest.fixture
def votos_crudos() -> pd.DataFrame:
    """Tres filas con conv_metadata anidado, como llega de load_raw (fixture propio de este archivo)."""

    def meta(a, b, h2_a=0, lista_a=0, negrita_a=0):
        return {
            "sum_assistant_a_tokens": a,
            "sum_assistant_b_tokens": b,
            "sum_user_tokens": 10,
            "header_count_a": {"h1": 0, "h2": h2_a},
            "header_count_b": {"h1": 0, "h2": 0},
            "list_count_a": {"ordered": 0, "unordered": lista_a},
            "list_count_b": {"ordered": 0, "unordered": 0},
            "bold_count_a": {"**": negrita_a, "__": 0},
            "bold_count_b": {"**": 0, "__": 0},
        }

    return pd.DataFrame({"conv_metadata": [meta(200, 100, 2, 3, 4), meta(50, 50), meta(0, 300)]})


def test_las_tres_formas_de_aplanar_dan_lo_mismo(votos_crudos):
    a = aplanar_iterrows(votos_crudos)
    b = aplanar_comprension(votos_crudos)
    c = aplanar_json_normalize(votos_crudos)
    pd.testing.assert_frame_equal(a, b)
    pd.testing.assert_frame_equal(b, c, check_like=True)   # json_normalize ordena distinto las columnas


def test_aplanar_coincide_con_el_aplanador_del_pipeline(votos_crudos):
    esperado = AplanadorConvMetadata().ajustar_transformar(votos_crudos)
    pd.testing.assert_frame_equal(aplanar_comprension(votos_crudos), esperado[list(aplanar_comprension(votos_crudos).columns)])


def test_json_normalize_no_fija_el_esquema_pero_el_aplanador_si(votos_crudos):
    incompleto = votos_crudos.copy()
    incompleto["conv_metadata"] = [{"sum_user_tokens": 1}] * 3
    paso = AplanadorConvMetadata().ajustar(votos_crudos)
    assert "header_a_h2" in paso.transformar(incompleto).columns      # esquema aprendido
    assert "header_a_h2" not in aplanar_json_normalize(incompleto).columns


@pytest.mark.parametrize("profundidad", [0, 1, 5, 50])
def test_recorrido_recursivo_e_iterativo_coinciden(profundidad):
    x = anidar(profundidad)
    assert recorrer_recursivo(x) == recorrer_iterativo(x)


def test_recorrido_iterativo_con_hoja_suelta_y_vacio():
    assert recorrer_iterativo(7) == [((), 7)]
    assert recorrer_iterativo({}) == []


def test_la_recursion_falla_con_anidamiento_muy_profundo_y_la_iteracion_no():
    x = anidar(2000)
    with pytest.raises(RecursionError):
        recorrer_recursivo(x)
    assert len(recorrer_iterativo(x)) > 2000


def test_las_tres_formas_de_sumar_formato_coinciden(votos_crudos):
    plano = AplanadorConvMetadata().ajustar_transformar(votos_crudos)
    columnas = columnas_formato(plano, "a")
    assert columnas, "debería haber columnas header_a_*, list_a_* y bold_a_*"
    esperado = formato_vectorizado(plano, columnas)
    assert list(esperado) == [9, 0, 0]
    pd.testing.assert_series_equal(formato_bucle(plano, columnas), esperado)
    pd.testing.assert_series_equal(formato_apply(plano, columnas), esperado)


def test_medir_por_tamano_y_exponente():
    datos = pd.DataFrame({"x": range(2000)})
    tabla = medir_por_tamano({"suma": lambda d: d["x"].sum()}, datos, [100, 500, 2000], repeticiones=2)
    assert list(tabla["n"]) == [100, 500, 2000]
    assert set(exponente(tabla).columns) == {"exponente_tiempo", "exponente_memoria"}


def test_medir_por_tamano_con_entrada_armada():
    tabla = medir_por_tamano({"r": recorrer_recursivo}, None, [1, 3], armar=lambda _, n: anidar(n), repeticiones=1)
    assert list(tabla["n"]) == [1, 3]


def test_json_con_esquema_coincide_exacto_con_el_aplanador(votos_crudos):
    paso = AplanadorConvMetadata().ajustar(votos_crudos)
    esquema = paso.parametros["columnas"]
    esperado = aplanar_comprension(votos_crudos)
    pd.testing.assert_frame_equal(aplanar_json_con_esquema(votos_crudos, esquema), esperado)


def test_json_con_esquema_conserva_las_columnas_aunque_falten_claves(votos_crudos):
    esquema = AplanadorConvMetadata().ajustar(votos_crudos).parametros["columnas"]
    incompleto = votos_crudos.copy()
    incompleto["conv_metadata"] = [{"sum_user_tokens": 1}] * 3
    salida = aplanar_json_con_esquema(incompleto, esquema)
    assert list(salida.columns) == esquema
    assert salida["header_a_h2"].isna().all()
