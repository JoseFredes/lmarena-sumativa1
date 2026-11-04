from arena.env import environment_info


def test_environment_info_has_expected_keys():
    info = environment_info()
    assert set(info) == {"python", "numpy", "pandas", "interpreter"}
    assert all(isinstance(v, str) and v for v in info.values())
