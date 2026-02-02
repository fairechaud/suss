import json
from argparse import Namespace
from pathlib import Path

from suss.commands.init import init as init_cmd
from suss.commands.testcase import create as create_cmd
from suss.handlers.repo import SussContext
from suss.handlers.indexer import load_index, save_index
from suss.misc import exit_codes


def _write_draft(path: Path) -> None:
    path.write_text(
        "---\n"
        "id: TC123456\n"
        "title: Alpha - Beta\n"
        "tags: smoke, api\n"
        "---\n\n"
        "## Steps\n"
        "1. Do thing\n",
        encoding="utf-8",
    )


def test_init_uses_cwd_when_repo_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    args = Namespace(repo=None)
    code = init_cmd(args)

    assert code == exit_codes.EXIT_OK
    assert (tmp_path / "suss.yaml").exists()


def test_create_with_group_writes_under_group(tmp_path: Path) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    args = Namespace(input=str(draft), group="PDM_270", context=context)
    code = create_cmd(args)

    assert code == exit_codes.EXIT_OK

    expected_key = "alpha_beta_123456"
    expected_path = repo_root / "specs" / "testcases" / "PDM_270" / f"{expected_key}.md"
    assert expected_path.exists()

    index_path = repo_root / ".suss" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert index["testcases"][0]["group"] == "PDM_270"
    index_path_value = index["testcases"][0]["path"].replace("\\", "/")
    assert index_path_value.endswith(f"specs/testcases/PDM_270/{expected_key}.md")


def test_create_without_group_writes_to_root(tmp_path: Path) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    args = Namespace(input=str(draft), group=None, context=context)
    code = create_cmd(args)

    assert code == exit_codes.EXIT_OK

    expected_key = "alpha_beta_123456"
    expected_path = repo_root / "specs" / "testcases" / f"{expected_key}.md"
    assert expected_path.exists()


def test_create_rejects_duplicate_id_and_does_not_write(tmp_path: Path) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    index_path = repo_root / ".suss" / "index.json"
    index = load_index(index_path)
    index["testcases"].append(
        {
            "id": "TC123456",
            "key": "existing_key",
            "title": "Existing",
            "tags": "smoke",
            "group": "PDM_270",
            "path": "specs/testcases/PDM_270/existing_key.md",
            "created": "2026-01-01T00:00:00+00:00",
            "updated": "2026-01-01T00:00:00+00:00",
            "fingerprint": "deadbeef",
        }
    )
    save_index(index_path, index)

    args = Namespace(input=str(draft), group="PDM_270", context=context)
    code = create_cmd(args)

    assert code == exit_codes.EXIT_REPO_ERROR

    expected_key = "alpha_beta_123456"
    expected_path = repo_root / "specs" / "testcases" / "PDM_270" / f"{expected_key}.md"
    assert not expected_path.exists()


def test_create_rejects_duplicate_fingerprint_and_does_not_write(tmp_path: Path) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    index_path = repo_root / ".suss" / "index.json"
    index = load_index(index_path)
    index["testcases"].append(
        {
            "id": "OTHER_ID",
            "key": "existing_key",
            "title": "Existing",
            "tags": "smoke",
            "group": "PDM_270",
            "path": "specs/testcases/PDM_270/existing_key.md",
            "created": "2026-01-01T00:00:00+00:00",
            "updated": "2026-01-01T00:00:00+00:00",
            "fingerprint": "6efa4a8a7afdc3c235cb18170aad948ab9b04e44",
        }
    )
    save_index(index_path, index)

    args = Namespace(input=str(draft), group="PDM_270", context=context)
    code = create_cmd(args)

    assert code == exit_codes.EXIT_REPO_ERROR

    expected_key = "alpha_beta_123456"
    expected_path = repo_root / "specs" / "testcases" / "PDM_270" / f"{expected_key}.md"
    assert not expected_path.exists()


def test_create_returns_io_error_on_missing_input(tmp_path: Path) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)
    args = Namespace(input=str(repo_root / "missing.md"), group=None, context=context)
    code = create_cmd(args)
    assert code == exit_codes.EXIT_IO_ERROR


def test_create_does_not_update_index_when_write_fails(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    def _boom(*_args, **_kwargs):
        raise OSError("write failed")

    monkeypatch.setattr("suss.commands.testcase.write_text", _boom)

    args = Namespace(input=str(draft), group="PDM_270", context=context)
    code = create_cmd(args)

    assert code == exit_codes.EXIT_IO_ERROR

    index_path = repo_root / ".suss" / "index.json"
    assert not index_path.exists()
