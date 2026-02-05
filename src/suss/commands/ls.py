import json
from pathlib import Path
from suss.misc.exit_codes import IndexStatus, ListStatus, ReadStatus
from suss.handlers.io import read_text
from suss.handlers.matcher import parse_csv, match_any, match_all
from suss.handlers.indexer import load_index

from linktoolsapi.logger import LinkLogger
_log = LinkLogger(__name__)

def _merge(matches: set[str] | None, matched: set[str], mode: str = "any") -> set[str]:
    if matches is None:
        return matched
    return (matches | matched) if mode == "any" else (matches & matched)

def _render_short(records: list[str]):
    for r in records:
        print(f"{r['id']} | {r['title']} | {r['tags']} | {r['group']}")

def _render_verbose(repo_root: Path, records: list[str]) -> None:
    for r in records:
        text = read_text(repo_root / r["path"], encoding="utf-8")
        print("\n" + text)

def _render_json(records: list[str]) -> None:
    print(json.dumps(records, indent=2))

def ls(args) -> tuple[int, str]:
    # Normalise args
    groups = args.group or None
    ids = args.id or None
    tags = args.tags or None
    patterns = args.search or None

    query_mode = args.query_mode or "any"
    tag_mode = args.tag_mode or "any"
    stdout_mode = args.stdout or "quiet"
    search_mode = args.search_mode or "any"
    limit = args.limit or 5

    _str = ""
    matches = None
    index = load_index(args.context.get_index_file())
    if not index["testcases"]:
        _str = "there are no testcases available to browse, import or create tests via 'suss tc new [INPUT]'"
        if "_missing" in index and index["_missing"]:
            _str = "no records can be found, make sure to run 'suss index' or point to a source of truth via --repo [PATH] flag"
        return IndexStatus.MISSING_INDEX, _str

    # List
    try:
        if groups:
            matched = {tc["path"] for tc in index["testcases"] if match_any(field_to_match=tc["group"], criteria=parse_csv(groups))}
            matches = _merge(matches, matched, query_mode)

        if ids:
            matched = {tc["path"] for tc in index["testcases"] if match_any(field_to_match=tc["id"], criteria=parse_csv(ids))}
            matches = _merge(matches, matched, query_mode)

        if tags:
            if tag_mode == "any":
                matched = {tc["path"] for tc in index["testcases"] if match_any(field_to_match=tc["tags"], criteria=parse_csv(tags))}
                matches = _merge(matches, matched, query_mode)
            elif tag_mode == "all":
                matched = {tc["path"] for tc in index["testcases"] if match_all(field_to_match=tc["tags"], criteria=parse_csv(tags))}
                matches = _merge(matches, matched, query_mode)
            else: 
                _str += f"bad arg value = {tag_mode}, options are [any|all]"
                return ReadStatus.INVALID_TAG, _str
        if patterns:
            if search_mode == "any":
                _str += "search:lazy"
            elif search_mode == "all":
                _str += "search:greedy"
            else:
                _str += f"bad arg value = {search_mode}, options are [any|all]"
                return ReadStatus.INVALID_SEARCH, _str
        if not matches:
            return ListStatus.NO_MATCH, "no matches were found for specified criteria"

        ordered = [tc for tc in index["testcases"] if tc["path"] in matches]
        if limit is not None:
            ordered = ordered[:limit]
        # Show / Output
        if stdout_mode not in {"quiet", "short", "verbose", "json"}:
            _str += f"bad arg value = {stdout_mode}, options are [quiet|short|verbose|json]"
            return ReadStatus.INVALID_OUTPUT, _str
        if stdout_mode == "quiet":
            pass
        elif stdout_mode == "short":
            _render_short(records=ordered)
            pass
        elif stdout_mode == "verbose":
            _render_verbose(repo_root=args.context.get_repo_root(), records=ordered)
        elif stdout_mode == "json":
            _render_json(records=ordered)
        return ListStatus.OK,""
    except Exception as e:
        _str = str(e)
        _log.debug(_str)
        return ListStatus.UNEXPECTED, _str
    
