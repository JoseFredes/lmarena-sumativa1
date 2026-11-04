"""Dataset download and integrity checks for lmarena-ai/arena-human-preference-140k."""
import hashlib
import logging
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

logger = logging.getLogger(__name__)

REPO_ID = "lmarena-ai/arena-human-preference-140k"
# Resolved from this file so it works no matter where the notebook is launched.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CHECKSUMS_NAME = "CHECKSUMS.txt"


def sha256_of(path: Path, chunk_size: int = 1 << 20) -> str:
    """Return the SHA-256 hex digest of a file, reading it in chunks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def list_remote_files(repo_id: str = REPO_ID) -> list[str]:
    """List the parquet files of the dataset repository on Hugging Face."""
    files = HfApi().list_repo_files(repo_id, repo_type="dataset")
    return sorted(f for f in files if f.endswith(".parquet"))


def download_dataset(raw_dir: Path = RAW_DIR, repo_id: str = REPO_ID) -> list[Path]:
    """Download every parquet file into ``raw_dir``; files already present are reused."""
    raw_dir = Path(raw_dir)
    paths = []
    for name in list_remote_files(repo_id):
        target = raw_dir / name
        if target.exists():
            logger.info("Reusing %s", name)
            paths.append(target)
            continue
        logger.info("Downloading %s", name)
        paths.append(Path(hf_hub_download(repo_id, name, repo_type="dataset", local_dir=raw_dir)))
    return paths


def write_checksums(paths: list[Path], raw_dir: Path = RAW_DIR) -> Path:
    """Write ``CHECKSUMS.txt`` with one ``<sha256>  <relative path>`` line per file."""
    raw_dir = Path(raw_dir)
    lines = [f"{sha256_of(p)}  {Path(p).relative_to(raw_dir)}" for p in sorted(paths)]
    out = raw_dir / CHECKSUMS_NAME
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def verify_checksums(raw_dir: Path = RAW_DIR) -> dict[str, bool]:
    """Recompute each hash listed in ``CHECKSUMS.txt`` and report whether it matches."""
    raw_dir = Path(raw_dir)
    checksums = raw_dir / CHECKSUMS_NAME
    if not checksums.exists():
        raise FileNotFoundError(f"{checksums} not found; run write_checksums first")
    result = {}
    for line in checksums.read_text(encoding="utf-8").splitlines():
        expected, rel = line.split("  ", 1)
        target = raw_dir / rel
        result[rel] = target.exists() and sha256_of(target) == expected
    return result


def ensure_dataset(raw_dir: Path = RAW_DIR, repo_id: str = REPO_ID) -> dict[str, bool]:
    """Download what is missing and check every file against ``CHECKSUMS.txt``.

    If the checksums file is already versioned, it is the reference and is never rewritten.
    Raises ``RuntimeError`` if any file does not match.
    """
    raw_dir = Path(raw_dir)
    paths = download_dataset(raw_dir, repo_id)
    if not (raw_dir / CHECKSUMS_NAME).exists():
        write_checksums(paths, raw_dir)
    result = verify_checksums(raw_dir)
    bad = [name for name, ok in result.items() if not ok]
    if bad:
        raise RuntimeError(f"checksum mismatch for: {bad}")
    return result
