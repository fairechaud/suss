from pathlib import Path

from _pytest.doctest import DOCTEST_REPORT_CHOICE_UDIFF
import pytest

from suss.misc import exit_codes
from suss.handlers.indexer import check_for_duplicates, load_index, save_index


def test_check_for_duplicates_detects_id(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    index = load_index(index_path)
    index["testcases"].append(
        {"id": "TC1", "fingerprint": "aaa"}
    )
    save_index(index_path, index)
    
    code, msg = check_for_duplicates(index, {"id": "TC1"})
    assert not code
    assert "id=" in msg



def test_check_for_duplicates_detects_fingerprint(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    index = load_index(index_path)
    index["testcases"].append(
        {"id": "TC1", "fingerprint": "aaa"}
    )
    save_index(index_path, index)

    code, msg = check_for_duplicates(index, {"id": "TC2", "fingerprint": "aaa"})
    assert not code
    assert "fingerprint=" in msg
