import uuid
from pathlib import Path
from suss.handlers import io

def draft_markdown_via_editor(draft_path: Path) -> tuple[str, Path]:
  """
  Drafts markdown in the given path, opens editor, reads back text.
  """
  io.write_text(draft_path, _template_md())
  print(f"Editing draft in $EDITOR: {draft_path}")
  print("Tip: use Ctrl+S to Save and close editor to continue ...")

  io.launch_editor(draft_path)
  text = io.read_text(draft_path)
  return text, draft_path

def build_draft_path(drafts_dir: Path, group: str | None) -> Path:
  label = group if group else "nogroup"
  return drafts_dir / f"draft_{label}_{uuid.uuid4().hex}.md"

def _template_md() -> str:
    return """---
title:
tags:
created:
updated:
---

## Preconditions

## Steps

## Expected
"""
