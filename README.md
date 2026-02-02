# SUSS

## 1. Purpose

**SUSS** is a **CLI-first test case knowledge and cataloguing tool** designed for test engineers who work primarily with Markdown, Git, and terminal-based workflows. It features:

* Filesystem objects as the **canonical source of truth**
* Git for versioning and audit trail
* A **derived local index** for fast search, filtering, and validation
* Markdown as the **import/export interchange format** (stdin/stdout)

No GUI, no server, no external services.

---

## 2. Design Principles

1. **File-first, Git-native**

   * Every test case and suite is a physical file
   * Git history is the audit trail

2. **CLI consistency**

   * Follows company CLI conventions (subcommands, argparse, interactive default)
   * Predictable flags and defaults

3. **Markdown round-trip**

   * Import test cases from stdin
   * Export test cases to stdout

4. **Derived index**

   * Index is rebuildable and disposable
   * Never treated as source of truth

5. **Minimal dependencies**

   * Python 3.11
   * Small runtime footprint (org logger + rich)

---

## 3. Non-Goals (MVP)

* No GUI or TUI
* No network/server mode
* No concurrent multi-user coordination
* No heavy analytics or dashboards
* No direct execution of tests (this is *not* a runner)

---

## 4. Repository Layout

```
<repo-root>/
  suss.yaml                  # repo config & root marker
  specs/
    testcases/
      <group>/
        <id>.md
    suites/
      <suite-id>.md
  runs/                       # optional, v0.3+
  .suss/
    index.json                # derived, gitignored
```

---

## 5. Object Model

### 5.1 TestCase

* One test case per file
* Markdown with YAML front matter
* Stable globally-unique `id`

**Required front matter fields**:

* `id: str`
* `title: str`
* `tags: str` (comma-separated)
* `created: ISO8601`
* `updated: ISO8601`

Body is freeform Markdown.

---

### 5.2 Suite

* Ordered list of TestCase IDs
* Stored as Markdown
* References test cases by ID only

---

### 5.3 Index (Derived)

* Generated via `suss index`
* Stored in `.suss/index.json`
* Contains:

  * Parsed metadata
  * Normalized text blobs
  * Fingerprints for similarity detection

Index may be deleted and regenerated at any time.

---

## 6. CLI Structure

```
python suss.py [subcommand] [options]
```

* If **no subcommand** is provided, tool enters **interactive mode**
* Subcommands map to logical domains (`tc`, `suite`, `index`, `search`)

---

## 7. MVP Feature Set

### Current state (v0.2 snapshot)

* Repo initialization
* Test case creation from editor or from an existing draft file
* Derived index updates on new test cases (duplicate id/fingerprint checks)
* Basic parser/validation for front matter

Notes:
* Legacy markdown without front matter is not supported.
* `suss index` exists, but only `suss tc new` currently updates the index; full rebuild scanning is still in progress.

### Deferred

* `suss tc list` (list + filter)
* `suss tc show`, `suss tc tag add/remove`
* Markdown import/export (stdin/stdout)
* Suite creation and management
* Search
* Execution runs
* Evidence attachment
* Statistics and flakiness analysis
* SQLite backend

---

## 8. Known Limitations

* Git merge conflicts possible on concurrent edits
* No transactional guarantees across multiple file writes
* Index can become stale (must be regenerated)
* Search is "good enough", not semantic
* CLI global flags must appear before subcommands (argparse)

---

## 9. Upgrade Path

* JSON index → SQLite index (transparent)
* Filesystem backend → DB backend
* CLI UX remains stable across upgrades

---

## 10. Definition of Done (MVP)

* Entire workflow usable without leaving terminal
* All data human-readable in Git
* Full help available via `-h`
* Deterministic, scriptable behavior

---

## 11. Roadmap (near-term)

1. Implement `suss tc list` with filters and index-backed output
2. Implement full `suss index` rebuild (scan repo, validate, de-dupe)
3. Add suite workflows (`suss suite new/add/remove/show`)
4. Add `suss tc show` and tag management commands
5. Web-based client for browsing and authoring test cases (optional)

---

## 12. Testing

Test coverage uses pytest and includes:
* Handler unit tests (parser, indexer, repo)
* Command workflow tests (direct function calls)
* CLI wiring tests (calling `suss.cli.main(argv)`)
* Negative and edge case coverage
