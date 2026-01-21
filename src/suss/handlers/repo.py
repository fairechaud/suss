from dataclasses import dataclass
from functools import wraps
from pathlib import Path

from suss.misc import exit_codes

REPO_MARKER = "suss.yaml"   # file that defines a SUSS repo root

STATE_DIRNAME = ".suss"     # tool state/cache (gitignored)
DRAFTS_DIRNAME = "drafts"
INDEX_FILENAME = "index.json"

SPECS_DIRNAME = "specs"
TESTCASES_DIRNAME = "testcases"
SUITES_DIRNAME = "suites"


def find_repo_root(start: Path) -> Path | None:
    """
    Walk upward from `start` looking for a directory containing REPO_MARKER.
    Returns the repo root path, or None if not found.
    """
    current = start.resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / REPO_MARKER).is_file():
            return candidate

    return None


def require_repo_root(start: Path) -> Path:
    """
    Like find_repo_root(), but raises if not found.
    """
    root = find_repo_root(start)
    if root is None:
        raise ValueError(
            f"Not inside a SUSS repo (missing {REPO_MARKER}). "
            "Run `suss init` or pass --repo <path>."
        )
    return root


def ensure_drafts(repo_root: Path) -> Path:
    """
    Returns <repo_root>/.suss/drafts and ensures it exists.
    """
    drafts = repo_root / STATE_DIRNAME / DRAFTS_DIRNAME
    drafts.mkdir(parents=True, exist_ok=True)
    return drafts

def requires_repo_root(handler_function):
    """
    Decorator for CLI handlers that require an existing SUSS repo.

    Behavior:
    - Uses args.repo if present, otherwise uses current working directory.
    - Walks upward to find suss.yaml.
    - If not found: prints error and returns EXIT_REPO_ERROR.
    - If found: runs handler.

    Optionally stashes resolved root on args as args.repo_root.
    """
    @wraps(handler_function)
    def wrapper(args, *other_args, **kwargs) -> int:
        repo_override = getattr(args, "repo", None)
        start_path = Path(repo_override) if repo_override else Path.cwd()

        root = find_repo_root(start_path)
        if root is None:
            print(f"Error: not inside a SUSS repo (missing {REPO_MARKER}).")
            print("Hint: run `suss init` or pass --repo <path>.")
            return exit_codes.EXIT_REPO_ERROR

        # handy for downstream code; avoids re-discovery
        setattr(args, "repo_root", root)

        return handler_function(args, *other_args, **kwargs)

    return wrapper

@dataclass(frozen=True)
class SussPaths:
    """
    Canonical project layout for a given SUSS repo root.
    """
    repo_root: Path

    @property
    def marker_file(self) -> Path:
        return self.repo_root / REPO_MARKER

    @property
    def state_dir(self) -> Path:
        return self.repo_root / STATE_DIRNAME

    @property
    def drafts_dir(self) -> Path:
        return self.state_dir / DRAFTS_DIRNAME

    @property
    def index_file(self) -> Path:
        return self.state_dir / INDEX_FILENAME

    @property
    def specs_dir(self) -> Path:
        return self.repo_root / SPECS_DIRNAME

    @property
    def testcases_dir(self) -> Path:
        return self.specs_dir / TESTCASES_DIRNAME

    @property
    def suites_dir(self) -> Path:
        return self.specs_dir / SUITES_DIRNAME

    def ensure_dirs(self) -> None:
        """
        Ensure standard directories exist. Safe to call multiple times.
        """
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        self.testcases_dir.mkdir(parents=True, exist_ok=True)
        self.suites_dir.mkdir(parents=True, exist_ok=True)


def init_repo(target_dir: Path) -> Path:
    """
    Initialize a new SUSS repo at target_dir.

    Creates:
      - suss.yaml
      - .suss/
      - .suss/drafts/
      - specs/testcases/
      - specs/suites/

    Returns the repo root.
    """
    repo_root = target_dir.resolve()
    paths = SussPaths(repo_root)

    repo_root.mkdir(parents=True, exist_ok=True)

    if paths.marker_file.exists():
        raise ValueError(f"SUSS repo already initialized (found {REPO_MARKER} at {paths.marker_file}).")

    paths.ensure_dirs()

    # Minimal marker file contents
    marker_text = "version: 0.1\ntool: suss\n"
    paths.marker_file.write_text(marker_text, encoding="utf-8")

    return repo_root
