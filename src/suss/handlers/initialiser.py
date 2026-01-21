from pathlib import Path

from suss.handlers.repo import SussPaths
from suss.misc import exit_codes

def init_repo(repo_root: Path) -> Path:
    repo_root = repo_root.resolve()
    paths = SussPaths(repo_root)
    repo_root.mkdir(parents=True, exist_ok=True)

    if paths.marker_file.exists():
        raise ValueError(f"SUSS repo already init'ed at {paths.marker_file}")

    paths.ensure_dirs()
    paths.marker_file.write_text("version: 0.1\ntool: suss\n", encoding="utf-8")
    return repo_root

