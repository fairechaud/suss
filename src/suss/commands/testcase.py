from pathlib import Path
from suss.misc import exit_codes
from suss.handlers.parser import (
    ParserException,
    identify_markdown_style,
    make_fingerprint_of_text,
    normalise_for_fingerprint,
    parse_markdown_draft_to_testcase,
    render_testcase_as_inline_string,
    render_testcase_to_text,
)
from suss.handlers.drafter import build_draft_path, draft_markdown_via_editor
from suss.handlers.io import write_text
from suss.handlers.indexer import check_for_duplicates, load_index, save_index

from linktoolsapi.logger import LinkLogger
_log = LinkLogger(__name__)

# Helpers
def _build_index_record(tc, group: str, dest_path: Path, fingerprint: str, repo_root: Path) -> dict:
  return {
      "id": tc.tc_id,
      "key": tc.key,
      "title": tc.title,
      "tags": tc.tags,
      "group": group or "",
      "path": str(dest_path.relative_to(repo_root)),
      "created": tc.created,
      "updated": tc.updated,
      "fingerprint": fingerprint
  }

# Commands
def create(args) -> int:
    """
    Wrapper for: suss tc create [input]

    Owns interpretation of args:
    - input omitted => launches editor for quick drafting
    - input == [filepath|dirpath] => reads file as stdin
    """
    text = "UNKNOWN"
    source = "UNKNOWN"
    fingerprint = "UNKNOWN"
    text_to_write = ""
    testcase = None
    group = getattr(args, "group", None)
    input_arg = getattr(args, "input", None)

    if input_arg is None:
        draft_path = build_draft_path(drafts_dir=args.context.get_drafts_target_path(), group=group)
        text, draft_path = draft_markdown_via_editor(draft_path=draft_path)
        source = f"editor={draft_path}"

        testcase = parse_markdown_draft_to_testcase(text, source=source)
        fingerprint = make_fingerprint_of_text(
            normalise_for_fingerprint(testcase.title) + "|" + normalise_for_fingerprint(testcase.body)
        )
        _log.info(f"SUCCESS : captured {len(text)} chars from {source}, group={group!r}")
    else:
        input_path = Path(input_arg)
        if not input_path.exists():
            _log.error("provided filepath doesn't exist")
            return exit_codes.EXIT_IO_ERROR
        testcase, fingerprint = identify_markdown_style(input_path)

    if not testcase:
        _log.error("testcase doesn't exist/is invalid")
        return exit_codes.EXIT_DATA_ERROR

    try:
        # Render markdown for file write
        text_to_write = render_testcase_to_text(tc=testcase,
                                                include_id=True,
                                                include_key=True,
                                                include_tags=True,
                                                include_body=True)
        _log.debug(f"{render_testcase_as_inline_string(tc=testcase)}")
        _log.debug(f"% {fingerprint}")

        # Build destination path
        dest_dir = args.context.get_testcases_target_path()
        if group:
            dest_dir = dest_dir / group
        filename = testcase.get_key()
        if not filename:
            _log.error(f"testcase key not found, check args")
            raise IOError("key for testcase doesn't exist")
        dest_path = dest_dir / f"{filename}.md"

        # Index record + duplicate check
        record = _build_index_record(
            tc=testcase,
            group=group,
            dest_path=dest_path,
            fingerprint=fingerprint,
            repo_root=args.context.get_repo_root()
        )

        # Store (write file first, then update index)
        index_path = args.context.get_index_file()
        index = load_index(index_path)
        check_for_duplicates(index, record)
        write_text(text=text_to_write, path=dest_path)
        index["testcases"].append(record)
        save_index(index_path, index)
        _log.info(f"SUCCESS : checkout {dest_path}")

    except ParserException as e:
        _log.error(str(e))
        return exit_codes.EXIT_DATA_ERROR

    except ValueError as e:
        _log.error(str(e))
        return exit_codes.EXIT_REPO_ERROR

    except Exception as e:
        _log.error(e)
        return exit_codes.EXIT_IO_ERROR

    return exit_codes.EXIT_OK
