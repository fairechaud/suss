from argparse import Namespace
from pathlib import Path

import pytest

from suss.handlers.repo import get_repo_context


def test_get_repo_context_requires_marker(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    args = Namespace(repo=None)
    with pytest.raises(ValueError):
        get_repo_context(args)


def test_get_repo_context_with_repo_flag_requires_marker(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    args = Namespace(repo=str(repo))
    with pytest.raises(ValueError):
        get_repo_context(args)
