from pathlib import Path

from suss.misc import exit_codes
from suss.handlers.initialiser import init_repo

from linktoolsapi.logger import LinkLogger
_log = LinkLogger(__name__)

def init(args) -> int:
    # TODO: args.repo override
    try:
        root = init_repo(Path(args.repo) if args.repo else Path.cwd())
        _log.debug(f"Done initialising SUSS repo at: {root}")
        return exit_codes.EXIT_OK
    except ValueError as e:
        _log.debug(str(e))
        return exit_codes.EXIT_REPO_ERROR
    
