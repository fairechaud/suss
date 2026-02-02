from pathlib import Path
from suss.handlers.repo import SussPaths
from dataclasses import asdict
from pathlib import Path
from datetime import datetime, timezone

from suss.handlers.io import read_json, write_json

def _now_iso() -> str:
  return datetime.now(timezone.utc).isoformat()

def load_index(index_path: Path) -> dict:
  """Load the index JSON, or return a new empty index payload."""
  if not index_path.exists():
      return {
          "meta": {"version": "0.2", "generated_at": _now_iso()},
          "testcases": []
      }
  return read_json(index_path)

def save_index(index_path: Path, index: dict) -> None:
  """Persist the index JSON and stamp a new generated_at timestamp."""
  index["meta"]["generated_at"] = _now_iso()
  write_json(index_path, index)

def check_for_duplicates(index: dict, record: dict) -> None:
  """Raise ValueError if the incoming record conflicts by id or fingerprint."""
  tc_id = record.get("id", "")
  fp = record.get("fingerprint", "")
  if not tc_id and not fp:
      return
  for existing in index.get("testcases", []):
      if tc_id and existing.get("id") == tc_id:
          raise ValueError(f"duplicate testcase detected (id={tc_id})")
      if fp and existing.get("fingerprint") == fp:
          raise ValueError(f"duplicate testcase detected (fingerprint={fp})")

def add_testcase_to_index(index_path: Path, record: dict) -> None:
  """Append a testcase record to the index after duplicate checks."""
  index = load_index(index_path)
  check_for_duplicates(index, record)

  index["testcases"].append(record)
  save_index(index_path, index)

def index_repo(repo_root: Path) -> None:
    paths = SussPaths(repo_root)
    paths.ensure_dirs()
