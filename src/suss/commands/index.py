from pathlib import Path

from suss.misc import exit_codes
from suss.handlers.repo import require_repo_root, SussPaths
from suss.handlers.indexer import index_repo

def index(args) -> int:
    try:
        repo_root = require_repo_root(Path.cwd())
    except ValueError as e:
        print(str(e))
        return exit_codes.EXIT_REPO_ERROR

    index_repo(repo_root)
    print(f"Indexed repo: {repo_root}")
    print(f"Index file: {SussPaths(repo_root).index_file}")
    return exit_codes.EXIT_OK

