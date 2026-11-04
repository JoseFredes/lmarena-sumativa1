"""Environment helpers: record how and where a notebook runs, for reproducibility."""
import csv
import json
import platform
import subprocess
import sys
from datetime import date
from importlib import metadata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
SEED = 42
DATASET_URL = "https://huggingface.co/datasets/lmarena-ai/arena-human-preference-140k"


def read_requirements(path: Path = REQUIREMENTS) -> dict[str, str]:
    """Parse ``name==version`` lines of a requirements file into ``{name: pinned_version}``."""
    pinned = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if "==" in line:
            name, version = line.split("==", 1)
            pinned[name.strip()] = version.strip()
    return pinned


def dependency_versions(requirements: Path = REQUIREMENTS) -> dict[str, dict[str, str | bool]]:
    """Installed vs. pinned version of every declared dependency.

    A missing package is reported as ``installed = "not installed"`` instead of raising.
    """
    result = {}
    for name, pinned in read_requirements(requirements).items():
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            installed = "not installed"
        result[name] = {"pinned": pinned, "installed": installed, "match": installed == pinned}
    return result


def git_info(root: Path = PROJECT_ROOT) -> dict[str, str]:
    """Current branch, short commit and whether the working tree is clean (or ``unknown``)."""
    def run(*args: str) -> str:
        try:
            out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)
            return out.stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return "unknown"

    status = run("status", "--porcelain")
    return {
        "branch": run("branch", "--show-current"),
        "commit": run("rev-parse", "--short", "HEAD"),
        "clean": "unknown" if status == "unknown" else str(status == ""),
    }


def environment_info() -> dict:
    """Python, OS, active interpreter, seed, git state and every declared dependency."""
    return {
        "python": sys.version.split()[0],
        "system": f"{platform.system()} {platform.release()}",
        "interpreter": sys.executable,
        "virtual_env": sys.prefix != sys.base_prefix,
        "seed": SEED,
        "git": git_info(),
        "dependencies": dependency_versions(),
    }


def write_phase_metadata(path: Path, phase: str, project: str = "¿Contenido o formato? Preferencias humanas en LMArena") -> Path:
    """Write a JSON snapshot of the environment for a phase (like the course model project)."""
    info = environment_info()
    payload = {
        "proyecto": project,
        "fase": phase,
        "fecha_ejecucion": date.today().isoformat(),
        "semilla": info["seed"],
        "python": info["python"],
        "sistema": info["system"],
        "entorno_virtual": info["virtual_env"],
        "git": info["git"],
        "dependencias": {k: v["installed"] for k, v in info["dependencies"].items()},
        "dataset": {"titulo": "arena-human-preference-140k", "url": DATASET_URL},
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_project_metadata(path: Path, decisions: dict[str, str] | None = None) -> Path:
    """Write ``key,value`` project metadata, with one ``decisiones.*`` row per decision."""
    rows = {
        "proyecto.nombre": "¿Contenido o formato? Preferencias humanas en LMArena",
        "proyecto.semilla": str(SEED),
        "datos.fuente.plataforma": "Hugging Face",
        "datos.fuente.autor": "lmarena-ai",
        "datos.fuente.url": DATASET_URL,
        "datos.licencia": "Prompts CC-BY-4.0; respuestas segun cada proveedor",
    }
    rows.update({f"decisiones.{k}": v for k, v in (decisions or {}).items()})
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["clave", "valor"])
        writer.writerows(rows.items())
    return path
