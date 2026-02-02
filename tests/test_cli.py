from pathlib import Path

from suss.cli import main as cli_main
from suss.handlers.initialiser import init_repo
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


def test_cli_no_args_returns_ok() -> None:
    code = cli_main([])
    assert code == exit_codes.EXIT_OK


def test_cli_init_creates_marker(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    code = cli_main(["--repo", str(repo_root), "init"])
    assert code == exit_codes.EXIT_OK
    assert (repo_root / "suss.yaml").exists()


def test_cli_tc_new_with_repo_flag(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    init_repo(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    code = cli_main(["--repo", str(repo_root), "tc", "new", str(draft), "-g", "PDM_270"])
    assert code == exit_codes.EXIT_OK

    expected_key = "alpha_beta_123456"
    expected_path = repo_root / "specs" / "testcases" / "PDM_270" / f"{expected_key}.md"
    assert expected_path.exists()


def test_cli_unknown_command_returns_user_error() -> None:
    import pytest

    with pytest.raises(SystemExit) as exc:
        cli_main(["nope"])
    assert int(exc.value.code) == 2


def test_cli_tc_new_missing_repo_marker_returns_repo_error(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    draft = repo_root / "draft.md"
    _write_draft(draft)

    import pytest

    with pytest.raises(ValueError):
        cli_main(["--repo", str(repo_root), "tc", "new", str(draft), "-g", "PDM_270"])


def test_cli_tc_new_missing_input_returns_io_error(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    init_repo(repo_root)

    missing = repo_root / "missing.md"
    code = cli_main(["--repo", str(repo_root), "tc", "new", str(missing), "-g", "PDM_270"])
    assert code == exit_codes.EXIT_IO_ERROR
