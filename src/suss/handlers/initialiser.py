from pathlib import Path
from suss.misc.exit_codes import RepoStatus

from suss.handlers.repo import SussPaths

def init_repo(repo_root: Path) -> tuple[int, str]:
    repo_root = repo_root.resolve()
    paths = SussPaths(repo_root)
    repo_root.mkdir(parents=True, exist_ok=True)

    if paths.marker_file.exists():
        _str = f"SUSS repo already init'ed at {paths.marker_file}"
        return RepoStatus.ALREADY_EXISTS, _str

    paths.ensure_dirs()
    paths.marker_file.write_text("version: 0.1\ntool: suss\n", encoding="utf-8")
    _str = f"SUSS repo init'ed correctly at {paths.marker_file}"
    return RepoStatus.OK, _str
