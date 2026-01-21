from pathlib import Path

from suss.misc import exit_codes
from suss.handlers.initialiser import init_repo

def init(args) -> int:
    # TODO: args.repo override
    target = Path.cwd()
    try:
        root = init_repo(target)
        print(f"Init'ed SUSS repo at: {root}")
        return exit_codes.EXIT_OK
    except ValueError as e:
        print(str(e))
        return exit_codes.EXIT_REPO_ERROR
    
