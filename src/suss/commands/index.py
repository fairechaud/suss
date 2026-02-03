from suss.misc.exit_codes import IndexStatus

from linktoolsapi.logger import LinkLogger
_log = LinkLogger(__name__)

def index(args) -> tuple[int,str]:
    try:
        if args.repo:
            _str = f"Overriden repo: {args.repo}"
        else:
            _str = f"Indexed repo: {args.context.get_repo_root()}"
        _log.debug(f"Index file: {args.context.get_index_file()}")
        return IndexStatus.OK, _str
    except Exception as e:
        _str = str(e)
        return IndexStatus.UNEXPECTED, _str

