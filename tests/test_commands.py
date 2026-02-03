import json
import pytest
from argparse import Namespace
from pathlib import Path

from suss.commands.init import init as init_cmd
from suss.commands.index import index as index_cmd
from suss.commands.testcase import create as create_cmd
from suss.handlers import repo
from suss.handlers.parser import ParserException
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
    code, _ = init_cmd(args)

    assert code == exit_codes.UserStatus.OK
    assert (tmp_path / "suss.yaml").exists()


def test_create_with_group_writes_under_group(tmp_path: Path) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    args = Namespace(input=str(draft), group="PDM_270", context=context)
    code, _ = create_cmd(args)

    assert code == exit_codes.WriteStatus.OK

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
    code, _ = create_cmd(args)

    assert code == exit_codes.WriteStatus.OK

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
    code, _ = create_cmd(args)

    assert code == exit_codes.IndexStatus.DUPLICATE_FOUND

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
    code, _ = create_cmd(args)

    assert code == exit_codes.IndexStatus.DUPLICATE_FOUND

    expected_key = "alpha_beta_123456"
    expected_path = repo_root / "specs" / "testcases" / "PDM_270" / f"{expected_key}.md"
    assert not expected_path.exists()


def test_create_returns_io_error_on_missing_input(tmp_path: Path) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)
    args = Namespace(input=str(repo_root / "missing.md"), group=None, context=context)
    code, _ = create_cmd(args)
    assert code == exit_codes.ReadStatus.INVALID_INPUT


def test_create_does_not_update_index_when_write_fails(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    def _boom(*_args, **_kwargs):
        raise OSError("write failed")

    monkeypatch.setattr("suss.commands.testcase.write_text", _boom)

    args = Namespace(input=str(draft), group="PDM_270", context=context)
    code, _ = create_cmd(args)

    assert code == exit_codes.WriteStatus.WRITE_OPERATION_FAILED

    index_path = repo_root / ".suss" / "index.json"
    assert not index_path.exists()

def test_create_rejects_comma_separated_group_and_does_not_write(tmp_path: Path) -> None:
    repo_root = tmp_path
    context = SussContext(repo_root)

    draft = repo_root / "draft.md"
    group="PDM_XXX, PDM_YYY"
    _write_draft(draft)

    args = Namespace(input=str(draft), group=group, context=context)
    code, _ = create_cmd(args)

    assert code == exit_codes.ReadStatus.INVALID_GROUP

    expected_key = "alpha_beta_123456"
    expected_path = repo_root / "specs" / "testcases" / group 
    assert not expected_path.exists()

    index_path = repo_root / ".suss" / "index.json"
    assert not index_path.exists()

    expected_test_path = repo_root / "specs" / "testcases" / expected_key
    assert not expected_test_path.exists()

def test_init_returns_repo_status_ok(tmp_path: Path):
    code, _ = init_cmd(Namespace(repo=str(tmp_path)))
    assert code == exit_codes.RepoStatus.OK

def test_index_returns_index_status_ok(tmp_path: Path):
    context = SussContext(tmp_path)
    code, _ = index_cmd(Namespace(repo=None, context=context))
    assert code == exit_codes.IndexStatus.OK

def test_create_with_missing_title_is_not_allowed(tmp_path: Path):
    repo_root = tmp_path
    context = SussContext(tmp_path)
    draft = repo_root / "draft.md"
    draft.write_text("---\nid: TC1\ntags: smoke\n---\n\nBody", encoding="utf-8")
    code, _ = create_cmd(Namespace(input=str(draft), context=context))
    assert code == exit_codes.ParseStatus.TEST_CREATION_FAILED

def test_create_rejects_invalid_id(tmp_path: Path):
    repo_root = tmp_path
    context = SussContext(tmp_path)
    draft = repo_root / "draft.md"
    draft.write_text("---\nid: TC12345#\ntitle: Invalid TC ID\ntags:\n---\nBody", encoding="utf-8")
    code, _ = create_cmd(Namespace(input=str(draft), context=context))
    assert code == exit_codes.ParseStatus.TEST_CREATION_FAILED

def test_create_rejects_empty_markdown(tmp_path: Path):
    repo_root = tmp_path
    context = SussContext(tmp_path)
    draft = repo_root / "draft.md"
    draft.write_text("", encoding="utf-8")
    code, _ = create_cmd(Namespace(input=str(draft), context=context))
    assert code == exit_codes.ParseStatus.TEST_CREATION_FAILED

