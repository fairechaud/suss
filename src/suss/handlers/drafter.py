import uuid
from pathlib import Path

from suss.handlers.repo import ensure_drafts
from suss.handlers import io
from suss.misc import exit_codes

def draft_markdown_via_editor(repo_root: Path, group: str | None) -> tuple[str, Path]:
    """
    Creates a draft file under <repo_root>/.suss/drafts, opens editor, reads back input.
    Returns: (markdown text, draft_path)
    """
    drafts_location = ensure_drafts(repo_root)
    label = group if group else "nogroup"
    draft_path = drafts_location / f"draft_{label}_{uuid.uuid4().hex}.md"

    io.write_text(draft_path, _template_md())
    print(f"Editing draft in $EDITOR: {draft_path}")
    print(f"Tip: use Ctrl+S to Save and close editor to continue ...")

    io.launch_editor(draft_path)
    text = io.read_text(draft_path)
    return text, draft_path

def _template_md() -> str:
    return """---
id:
title:
tags: []
created:
updated:
---

## Intent

## Preconditions

## Steps

## Expected
"""
