from pathlib import Path

import pytest

from suss.handlers.indexer import check_for_duplicates, load_index, save_index


def test_check_for_duplicates_detects_id(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    index = load_index(index_path)
    index["testcases"].append(
        {"id": "TC1", "fingerprint": "aaa"}
    )
    save_index(index_path, index)

    with pytest.raises(ValueError):
        check_for_duplicates(index, {"id": "TC1"})


def test_check_for_duplicates_detects_fingerprint(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    index = load_index(index_path)
    index["testcases"].append(
        {"id": "TC1", "fingerprint": "aaa"}
    )
    save_index(index_path, index)

    with pytest.raises(ValueError):
        check_for_duplicates(index, {"id": "TC2", "fingerprint": "aaa"})
