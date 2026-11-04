import json

from arena.env import (
    dependency_versions,
    environment_info,
    git_info,
    read_requirements,
    write_phase_metadata,
    write_project_metadata,
)


def test_read_requirements_ignores_comments_and_unpinned(tmp_path):
    f = tmp_path / "req.txt"
    f.write_text("# header\nnumpy==1.0  # inline\npandas==2.0\nrequests\n", encoding="utf-8")
    assert read_requirements(f) == {"numpy": "1.0", "pandas": "2.0"}


def test_dependency_versions_flags_missing_and_mismatch(tmp_path):
    f = tmp_path / "req.txt"
    f.write_text("pytest==0.0.1\nno-such-package-xyz==1.0\n", encoding="utf-8")
    deps = dependency_versions(f)
    assert deps["pytest"]["match"] is False
    assert deps["no-such-package-xyz"]["installed"] == "not installed"


def test_project_requirements_are_installed_as_pinned():
    # Guards reproducibility: the active environment must match requirements.txt.
    assert all(d["match"] for d in dependency_versions().values())


def test_git_info_outside_a_repo_is_unknown(tmp_path):
    assert git_info(tmp_path) == {"branch": "unknown", "commit": "unknown", "clean": "unknown"}


def test_environment_info_keys():
    info = environment_info()
    assert {"python", "system", "interpreter", "virtual_env", "seed", "git", "dependencies"} <= set(info)
    assert info["seed"] == 42


def test_write_phase_metadata_is_valid_json(tmp_path):
    out = write_phase_metadata(tmp_path / "meta.json", "F1")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["fase"] == "F1" and data["semilla"] == 42 and "numpy" in data["dependencias"]


def test_write_project_metadata_rows(tmp_path):
    out = write_project_metadata(tmp_path / "meta.csv", {"dataset": "completo"})
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "clave,valor"
    assert "decisiones.dataset,completo" in lines
