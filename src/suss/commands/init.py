from pathlib import Path

from suss.misc.exit_codes import RepoStatus, UserStatus
from suss.handlers.initialiser import init_repo

from linktoolsapi.logger import LinkLogger
_log = LinkLogger(__name__)

def init(args) -> tuple[int, str]:
    # TODO: args.repo override
    try:
        code, msg = init_repo(Path(args.repo) if args.repo else Path.cwd())
        return code, msg
    except Exception as e:
        _str = str(e)
        _log.debug(_str)
        return RepoStatus.UNEXPECTED, _str
    
