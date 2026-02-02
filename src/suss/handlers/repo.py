from dataclasses import dataclass
from pathlib import Path

REPO_MARKER = "suss.yaml"   # file that defines a SUSS repo root

STATE_DIRNAME = ".suss"     # tool state/cache (gitignored)
DRAFTS_DIRNAME = "drafts"
INDEX_FILENAME = "index.json"

SPECS_DIRNAME = "specs"
TESTCASES_DIRNAME = "testcases"
SUITES_DIRNAME = "suites"

class SussContext:
    def __init__(self, repo_root) -> None:
        self.repo_paths = SussPaths(repo_root)
        self.repo_paths.ensure_dirs()

    def get_repo_root(self) -> Path:
        return self.repo_paths.repo_root

    def get_index_file(self) -> Path:
        return self.repo_paths.index_file

    def get_specs_target_path(self) -> Path:
        return self.repo_paths.specs_dir

    def get_suites_target_path(self) -> Path:
        return self.repo_paths.suites_dir

    def get_drafts_target_path(self) -> Path:
        return self.repo_paths.drafts_dir

    def get_testcases_target_path(self) -> Path:
        return self.repo_paths.testcases_dir

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

def get_repo_context(args) -> SussContext:
    """Resolve and validate a repo root, then return a populated SussContext."""
    if args.repo:
        repo_root = require_repo_root(Path(args.repo))
    else:
        repo_root = require_repo_root(Path.cwd())
    context = SussContext(repo_root)
    return context
    
    
