import sys
from pathlib import Path

from suss.misc import exit_codes
from suss.handlers.repo import require_repo_root
from suss.handlers.drafter import draft_markdown_via_editor

def create(args) -> int:
    """
    Wrapper for: suss tc create [input]

    Owns interpretation of args:
    - input omitted => launches editor for quick drafting
    - input == "-" => reads stdin
    - (later on): file/dir reading and parsing
    """

    group = getattr(args, "group", None)
    input_arg = getattr(args, "input", None)

    try:
        repo_root = require_repo_root(Path.cwd())
    except ValueError as e:
        print(str(e))
        return exit_codes.EXIT_REPO_ERROR

    if input_arg is None:
        text, draft_path = draft_markdown_via_editor(repo_root=repo_root, group=group)
        source = f"editor={draft_path}"
    elif input_arg == "-":
        text = _read_all_stdin()
        source = "stdin"
    else:
        print("tc create [filepath|dir] is not supported yet")

    # Prototype
    print(f"tc create captured {len(text)} chars from {source}, group={group!r}")
    print()
    print(text)
    print("EOF")
    return exit_codes.EXIT_OK

def _read_all_stdin() -> str:
    data = sys.stdin.read()
    if not data.strip():
        raise ValueError("stdin was empty")
    return data


