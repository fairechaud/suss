from suss.misc.exit_codes import IndexStatus, ListStatus, ReadStatus
from suss.handlers.matcher import parse_csv, match_any, match_all
from suss.handlers.indexer import load_index

from linktoolsapi.logger import LinkLogger
_log = LinkLogger(__name__)

def _merge(matches: set[str] | None, matched: set[str], mode: str = "any") -> set[str]:
    if matches is None:
        return matched
    return (matches | matched) if mode == "any" else (matches & matched)

def ls(args) -> tuple[int, str]:
    _str = ""
    matches = None
    index = load_index(args.context.get_index_file())
    if not index["testcases"]:
        _str = "there are no testcases available to browse, import or create tests via 'suss tc new [INPUT]'"
        if "_missing" in index and index["_missing"]:
            _str = "no records can be found, make sure to run 'suss index' or point to a source of truth via --repo [PATH] flag"
        return IndexStatus.MISSING_INDEX, _str
    try:
        if args.group:
            matched = {tc["path"] for tc in index["testcases"] if match_any(field_to_match=tc["group"], criteria=parse_csv(args.group))}
            matches = _merge(matches, matched, args.query_mode)

        if args.id:
            matched = {tc["path"] for tc in index["testcases"] if match_any(field_to_match=tc["id"], criteria=parse_csv(args.id))}
            matches = _merge(matches, matched, args.query_mode)

        if args.tags:
            if args.tag_mode == "any":
                matched = {tc["path"] for tc in index["testcases"] if match_any(field_to_match=tc["tags"], criteria=parse_csv(args.tags))}
                matches = _merge(matches, matched, args.query_mode)
            elif args.tag_mode == "all":
                matched = {tc["path"] for tc in index["testcases"] if match_all(field_to_match=tc["tags"], criteria=parse_csv(args.tags))}
                matches = _merge(matches, matched, args.query_mode)
            else: 
                _str += f"bad arg value = {args.tag_mode}, options are [any|all]"
                return ReadStatus.INVALID_TAG, _str
        if args.search:
            if args.search_mode == "any":
                _str += "search:lazy"
            elif args.search_mode == "all":
                _str += "search:greedy"
            else:
                _str += f"bad arg value = {args.search_mode}, options are [any|all]"
                return ReadStatus.INVALID_SEARCH, _str
        if not matches:
            return ListStatus.NO_MATCH, "no matches were found for specified criteria"

        # Presentation
        if args.stdout:
            if args.stdout == "quiet":
                return ListStatus.OK, f"found {len(matches)} result(s)"
            elif args.stdout == "short":
                return ListStatus.OK, f"here we print the inline representation (title + body)"
            elif args.stdout == "verbose":
                return ListStatus.OK, f"here we print every field in the right form"
            else:
                _str += f"bad arg value = {args.stdout}, options are [quiet|short|verbose]"
                return ReadStatus.INVALID_OUTPUT, _str
        return ListStatus.OK, f"found {len(matches)} result(s)"
    except Exception as e:
        _str = str(e)
        _log.debug(_str)
        return ListStatus.UNEXPECTED, _str
    
