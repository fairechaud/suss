from pathlib import Path
import os
import subprocess
import sys

def pick_editor() -> list[str]:
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if editor:
        return editor.split()
    if sys.platform.startswith("win"):
        return ["notepad"]
    return ["vi"]

def launch_editor(path: Path) -> int:
    cmd = pick_editor() + [str(path)]
    proc = subprocess.run(cmd, check=False)
    return int(proc.returncode)

def read_text(path: Path, encoding: str = "utf-8") -> str:
    return path.read_text(encoding=encoding)

def write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding=encoding)
