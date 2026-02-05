import json
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

def _cli_create_tc(repo_root: Path, title: str, tags: str, group: str | None, tc_id: str | None = None) -> None:
    draft = repo_root / f"draft_{title.lower().replace(' ', '_')}.md"
    draft.write_text(
            "---\n"
            + (f"id: {tc_id}\n" if tc_id else "")
            + f"title: {title}\n"
            + f"tags: {tags}\n"
            + "---\n\n"
            + "# Steps\n"
            + "1. Do a barrel roll",
            encoding="utf-8"
            )
    args = ["--repo", str(repo_root), "tc", "new", str(draft)]
    if group:
        args += ["-g", group]
    code = cli_main(args)
    assert code == exit_codes.WriteStatus.OK

def _populate_repo_with_stubs(tmp_path: Path) -> Path:
    init_repo(tmp_path)
    _cli_create_tc(tmp_path, title="Sample Test A", tags="", group="sample group", tc_id="TCID")
    _cli_create_tc(tmp_path, title="Sample Test B", tags="smoke", group="sample group", tc_id="999999")
    _cli_create_tc(tmp_path, title="Sample Test C", tags="regression", group=None, tc_id="XXXXXX")
    _cli_create_tc(tmp_path, title="Negative Happy Z", tags="smoke,regression", group="GROUP1", tc_id="ZZZZZZ")
    return tmp_path


def test_cli_no_args_returns_ok() -> None:
    code = cli_main([])
    assert code == exit_codes.UserStatus.OK


def test_cli_init_creates_marker(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    code = cli_main(["--repo", str(repo_root), "init"])
    assert code == exit_codes.RepoStatus.OK
    assert (repo_root / "suss.yaml").exists()

def test_cli_init_marker_already_exists() -> None:
    repo_root = Path("C:\\sandbox")
    code = cli_main(["--repo", str(repo_root), "init"])
    assert code == exit_codes.RepoStatus.ALREADY_EXISTS
    assert (repo_root / "suss.yaml").exists()


def test_cli_tc_new_with_repo_flag(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    init_repo(repo_root)

    draft = repo_root / "draft.md"
    _write_draft(draft)

    code = cli_main(["--repo", str(repo_root), "tc", "new", str(draft), "-g", "PDM_270"])
    assert code == exit_codes.WriteStatus.OK

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
    assert code == exit_codes.ReadStatus.INVALID_INPUT

def test_cli_list_group_id_any(tmp_path: Path, capsys):
    repo = _populate_repo_with_stubs(tmp_path)
    capsys.readouterr()
    cli_main(["--repo", str(repo), "list", "--group", "sample group", "--id", "TCID", "--stdout", "json"])
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 2

def test_cli_list_group_id_all(tmp_path: Path, capsys):
    repo = _populate_repo_with_stubs(tmp_path)
    capsys.readouterr()
    cli_main(["--repo", str(repo), "list", "--group", "sample group", "--id", "TCID", "--query-mode", "all", "--stdout", "json"])
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 1

def test_cli_list_group_and_tags_any(tmp_path: Path, capsys):
    repo = _populate_repo_with_stubs(tmp_path)
    capsys.readouterr()
    cli_main(["--repo", str(repo), "list", "--group", "sample group", "--tags", "smoke, regression", "--stdout", "json"])
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 4

def test_cli_list_tags_all(tmp_path: Path, capsys):
    repo = _populate_repo_with_stubs(tmp_path)
    capsys.readouterr()
    cli_main(["--repo", str(repo), "list", "--tag-mode", "all", "--tags", "smoke, regression", "--stdout", "json"])
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 1

def test_cli_list_tags_any(tmp_path: Path, capsys):
    repo = _populate_repo_with_stubs(tmp_path)
    capsys.readouterr()
    cli_main(["--repo", str(repo), "list", "--tags", "smoke, regression", "--stdout", "json"])
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 3

def test_cli_list_no_matches(tmp_path: Path, capsys):
    repo = _populate_repo_with_stubs(tmp_path)
    capsys.readouterr()
    code = cli_main(["--repo", str(repo), "list", "--group", "NOT_FOUND"])
    assert code == exit_codes.ListStatus.NO_MATCH


def test_cli_list_invalid_stdout(tmp_path: Path, capsys):
    import pytest
    repo = _populate_repo_with_stubs(tmp_path)
    capsys.readouterr()
    with pytest.raises(SystemExit) as exc:
        cli_main(["--repo", str(repo), "list", "--group", "sample group", "--stdout", "bad"])
    assert int(exc.value.code) == 2
