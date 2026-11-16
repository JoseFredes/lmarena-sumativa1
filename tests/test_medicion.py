"""Pruebas de medicion.py: medir, mejor_tiempo y comparar."""
import pytest

from arena.medicion import comparar, medir, mejor_tiempo


def test_medir_devuelve_resultado_tiempo_y_memoria():
    resultado, segundos, memoria = medir(sum, range(1000))
    assert resultado == 499500
    assert segundos >= 0
    assert memoria >= 0


def test_medir_pasa_args_y_kwargs():
    resultado, _, _ = medir(lambda a, b=0: a - b, 10, b=3)
    assert resultado == 7


def test_medir_reporta_mas_memoria_para_una_lista_grande():
    _, _, chica = medir(lambda: list(range(10)))
    _, _, grande = medir(lambda: list(range(1_000_000)))
    assert grande > chica


def test_medir_propaga_excepciones_y_deja_tracemalloc_apagado():
    import tracemalloc
    with pytest.raises(ZeroDivisionError):
        medir(lambda: 1 / 0)
    # si no se detuvo tracemalloc, la siguiente medición quedaría contaminada
    assert medir(sum, [1, 2])[0] == 3
    assert not tracemalloc.is_tracing()


def test_mejor_tiempo_es_el_minimo_de_las_repeticiones():
    assert mejor_tiempo(sum, range(100), repeticiones=3) >= 0


def test_comparar_arma_la_tabla_con_la_razon_de_lentitud():
    tabla = comparar({"suma": sum, "lista": lambda xs: sum(list(xs))}, range(10_000), repeticiones=2)
    assert list(tabla["implementacion"]) == ["suma", "lista"]
    assert {"segundos", "memoria_mb", "veces_mas_lenta"} <= set(tabla.columns)
    assert tabla["veces_mas_lenta"].min() == pytest.approx(1.0)
