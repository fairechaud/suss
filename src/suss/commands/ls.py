from suss.misc import exit_codes

from linktoolsapi.logger import LinkLogger
_log = LinkLogger(__name__)

def ls(args) -> int:
    try:
        _log.debug(f"you've called list with args: {args}")
        return exit_codes.EXIT_OK
    except Exception as e:
        _log.debug(str(e))
        return exit_codes.EXIT_REPO_ERROR
    
