"""Pruebas de Pipeline y de la equivalencia con el pipeline funcional de F2."""
import pandas as pd
import pytest

from arena.pipeline import Pipeline
from arena.preprocessing import convert_types, derive_variables, flatten
from arena.transformadores import ConversorTipo, pasos_f2, pasos_f3


def test_agregar_rechaza_lo_que_no_es_transformador():
    with pytest.raises(TypeError, match="Se esperaba un Transformador"):
        Pipeline().agregar("no soy un paso")


def test_agregar_devuelve_el_pipeline_y_permite_encadenar():
    pipe = Pipeline()
    assert pipe.agregar(ConversorTipo("x", "float64")) is pipe
    assert len(pipe) == 1


def test_transformar_antes_de_ajustar_falla(raw_anidado):
    with pytest.raises(RuntimeError, match="ajustar antes de transformar"):
        Pipeline(pasos_f2()).transformar(raw_anidado)


def test_pipeline_vacio_devuelve_una_copia_igual():
    df = pd.DataFrame({"x": [1, 2]})
    salida = Pipeline().ajustar(df).transformar(df)
    pd.testing.assert_frame_equal(salida, df)
    assert salida is not df


def test_ajustar_y_transformar_no_modifican_la_entrada(raw_anidado):
    copia = raw_anidado.copy(deep=True)
    Pipeline(pasos_f2()).ajustar(raw_anidado).transformar(raw_anidado)
    pd.testing.assert_frame_equal(raw_anidado, copia)


def test_resumen_y_repr(raw_anidado):
    pipe = Pipeline(pasos_f2())
    assert list(pipe.resumen().columns) == ["orden", "paso", "clase"]
    assert len(pipe.resumen()) == 7
    assert repr(pipe) == "Pipeline(7 pasos, sin ajustar)"
    pipe.ajustar(raw_anidado)
    assert repr(pipe) == "Pipeline(7 pasos, ajustado)"
    assert len(pipe.pasos_ejecutados()) == 7


def test_pasos_f2_equivale_al_pipeline_funcional_de_f2(raw_anidado):
    esperado = derive_variables(convert_types(flatten(raw_anidado)))
    obtenido = Pipeline(pasos_f2()).ajustar(raw_anidado).transformar(raw_anidado)
    pd.testing.assert_frame_equal(obtenido, esperado)


def test_pasos_f3_solo_cambia_dos_columnas_respecto_de_f2(raw_anidado):
    f2 = Pipeline(pasos_f2()).ajustar(raw_anidado).transformar(raw_anidado)
    f3 = Pipeline(pasos_f3()).ajustar(raw_anidado).transformar(raw_anidado)
    assert set(f2.columns) - set(f3.columns) == {"cat_creative_writing_score"}
    assert str(f3["cat_if_score"].dtype) == "Int8"
    pd.testing.assert_frame_equal(f3.drop(columns="cat_if_score"),
                                  f2.drop(columns=["cat_creative_writing_score", "cat_if_score"]))


def test_equivalencia_con_clean_dataset_sobre_datos_reales(tmp_path):
    """Con un archivo real de LMArena, las clases dan lo mismo que F2 (se omite si no hay datos)."""
    from shutil import copyfile
    from arena.io import RAW_DIR
    from arena.preprocessing import clean_dataset
    from arena.profile import load_raw

    archivos = sorted(RAW_DIR.rglob("train-00000-of-*.parquet"))
    if not archivos:
        pytest.skip("falta data/raw (corre `make data`)")
    
    copyfile(archivos[0], tmp_path / archivos[0].name)

    esperado = clean_dataset(tmp_path)
    crudo = load_raw(tmp_path)
    obtenido = Pipeline(pasos_f2()).ajustar(crudo).transformar(crudo)
    pd.testing.assert_frame_equal(obtenido, esperado)
