# SUSS – MVP Specification (Paradigm B++)

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

5. **No external dependencies**

   * Python 3.11
   * Standard library only

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
* `tags: list[str]`
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

### Included in v0.1

* Repo initialization
* Index generation
* Test case creation, listing, tagging
* Markdown import/export
* Suite creation and management
* Text search

### Deferred

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
