# TESTING

## Scope
This project uses pytest to cover the command workflows and the low-level handler logic.
Tests live under `tests/` and are designed to be fast and deterministic.

## Test Categories

### 1) Unit Tests (Handlers)
Focus: pure or low-level functions with clear inputs/outputs.
Examples:
- Indexer duplicate checks
- Repo marker validation
- Parser error paths

### 2) Workflow Tests (Commands)
Focus: orchestration and side effects.
We call `suss.commands.*` functions directly with a `Namespace` to simulate argparse.
Examples:
- `tc new` happy path (grouped and ungrouped)
- Duplicate id/fingerprint rejection
- Write failure does not update index

### 3) CLI Wiring Tests
Focus: argparse wiring and top-level behavior.
We call `suss.cli.main(argv)` to simulate real CLI usage without spawning a subprocess.
Examples:
- `init` with `--repo`
- `tc new` with `--repo` and `-g`
- Unknown command (argparse exits with status 2)

### 4) Negative / Edge Cases
Focus: error paths and boundary conditions.
Examples:
- Missing input path
- Missing repo marker
- Legacy markdown without front matter

## Running Tests
```
uv run pytest
```

## Conventions
- Prefer direct function calls for speed and determinism.
- Use `monkeypatch` only to force error paths (e.g., simulate failed writes).
- Keep assertions on filesystem side-effects explicit (file paths and index content).
