from pathlib import Path

import pytest

from suss.handlers.parser import ParserException, identify_markdown_style


def test_identify_markdown_style_rejects_legacy(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy.md"
    legacy.write_text("# No front matter\n\nBody", encoding="utf-8")

    with pytest.raises(ParserException):
        identify_markdown_style(legacy)
