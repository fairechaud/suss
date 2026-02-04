from pathlib import Path


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

def test_save_index_strips_missing_flag(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    index = {
            "meta": {"version": 0.2, "generated_at": "right_now"},
            "_missing": True,
            "testcases": []
            }
    save_index(index_path,index)
    saved = load_index(index_path)
    assert "_missing" not in saved

def test_load_index_sets_missing_flag_when_index_is_missing(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    index = load_index(index_path)
    assert index.get("_missing") is True
