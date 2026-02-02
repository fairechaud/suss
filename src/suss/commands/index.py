
from suss.misc import exit_codes

from linktoolsapi.logger import LinkLogger
_log = LinkLogger(__name__)

def index(args) -> int:
    try:
        if args.repo:
            _log.debug(f"Overriden repo: {args.repo}")
        else:
            _log.debug(f"Indexed repo: {args.context.get_repo_root()}")
        _log.debug(f"Index file: {args.context.get_index_file()}")
        return exit_codes.EXIT_OK
    except ValueError as e:
        _log.error(str(e))
        return exit_codes.EXIT_REPO_ERROR

