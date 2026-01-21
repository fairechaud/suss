from pathlib import Path
from suss.handlers.repo import SussPaths

def index_repo(repo_root: Path) -> None:
    paths = SussPaths(repo_root)
    paths.ensure_dirs()
