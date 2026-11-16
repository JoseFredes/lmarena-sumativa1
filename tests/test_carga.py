"""Pruebas de carga.py sin red: lectura por extensión, esquema y archivos locales."""
import pandas as pd
import pytest

from arena import carga
from arena.carga import (
    ARCHIVOS_PARQUET,
    COLUMNAS_ESPERADAS,
    asegurar_archivos,
    cargar,
    leer_archivo,
    verificar_esquema,
)


def test_leer_archivo_csv_y_parquet(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    df.to_csv(tmp_path / "t.csv", index=False)
    df.to_parquet(tmp_path / "t.parquet")
    assert leer_archivo(str(tmp_path / "t.csv")).shape == (2, 2)
    assert list(leer_archivo(str(tmp_path / "t.parquet"), columnas=["a"]).columns) == ["a"]


def test_leer_archivo_extension_desconocida_falla():
    with pytest.raises(ValueError, match="Extensión no reconocida"):
        leer_archivo("datos.json")


def test_verificar_esquema_informa_las_sobrantes():
    df = pd.DataFrame({"a": [1], "b": [2], "extra": [3]})
    assert verificar_esquema(df, ["a", "b"]) == {"declaradas": 2, "en_archivo": 3, "no_declaradas": ["extra"]}


def test_verificar_esquema_con_columna_faltante_falla():
    with pytest.raises(KeyError, match="Faltan columnas esperadas"):
        verificar_esquema(pd.DataFrame({"a": [1]}), ["a", "b"])


def test_cargar_archivo_inexistente_falla(tmp_path):
    with pytest.raises(FileNotFoundError):
        cargar(str(tmp_path / "no_existe.csv"), ["a"])


def test_cargar_fuerza_columnas_numericas(tmp_path):
    ruta = tmp_path / "t.csv"
    pd.DataFrame({"a": ["1", "2", "texto"], "b": ["x", "y", "z"]}).to_csv(ruta, index=False)
    df = cargar(str(ruta), ["a", "b"], columnas_numericas=["a"])
    assert df["a"].isna().sum() == 1             # el texto suelto pasa a NaN, no a columna de texto


def test_asegurar_archivos_usa_los_locales_sin_descargar(tmp_path, monkeypatch):
    for nombre in ARCHIVOS_PARQUET:
        destino = tmp_path / nombre
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.touch()

    def sin_red(**kwargs):
        raise AssertionError("no debería descargar si el archivo ya existe")

    monkeypatch.setattr(carga, "hf_hub_download", sin_red)
    rutas = asegurar_archivos(tmp_path)
    assert len(rutas) == 7 and all(r.exists() for r in rutas)


def test_asegurar_archivos_descarga_solo_los_que_faltan(tmp_path, monkeypatch):
    pedidos = []
    monkeypatch.setattr(carga, "hf_hub_download", lambda **kw: pedidos.append(kw["filename"]))
    asegurar_archivos(tmp_path)
    assert pedidos == ARCHIVOS_PARQUET


def test_columnas_esperadas_son_las_11_del_dato_crudo():
    assert len(COLUMNAS_ESPERADAS) == 11
