import hashlib

import pytest

from arena.io import CHECKSUMS_NAME, sha256_of, verify_checksums, write_checksums


def test_sha256_of_matches_hashlib(tmp_path):
    f = tmp_path / "a.bin"
    f.write_bytes(b"hello")
    assert sha256_of(f) == hashlib.sha256(b"hello").hexdigest()


def test_sha256_of_empty_file(tmp_path):
    f = tmp_path / "empty.bin"
    f.write_bytes(b"")
    assert sha256_of(f) == hashlib.sha256(b"").hexdigest()


def test_checksums_roundtrip(tmp_path):
    (tmp_path / "data").mkdir()
    f = tmp_path / "data" / "x.parquet"
    f.write_bytes(b"abc")
    out = write_checksums([f], tmp_path)
    assert out.name == CHECKSUMS_NAME
    assert verify_checksums(tmp_path) == {"data/x.parquet": True}


def test_verify_detects_modified_file(tmp_path):
    f = tmp_path / "x.parquet"
    f.write_bytes(b"abc")
    write_checksums([f], tmp_path)
    f.write_bytes(b"changed")
    assert verify_checksums(tmp_path) == {"x.parquet": False}


def test_verify_detects_missing_file(tmp_path):
    f = tmp_path / "x.parquet"
    f.write_bytes(b"abc")
    write_checksums([f], tmp_path)
    f.unlink()
    assert verify_checksums(tmp_path) == {"x.parquet": False}


def test_verify_without_checksums_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="CHECKSUMS.txt"):
        verify_checksums(tmp_path)
