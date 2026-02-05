# suss CLI Command Cheatsheet & Implementation Blueprint

This document enumerates **all intended MVP commands**, their purpose, inputs, outputs, and implementation notes.

All commands:
- Use `argparse`
- Support `-h / --help`
- Exit non-zero on error
- Are safe to script (stdin/stdout, no hidden prompts unless interactive mode)

---

## Global Invocation

```
python suss.py [subcommand] [options]
```

If no subcommand is provided -> **interactive mode**.

---

## Interactive Mode (default)

```
python suss.py
```

Behavior:
- Detect repo root
- Present numbered menu:
  1. List test cases
  2. Search
  3. Create test case
  4. Manage suites
- Uses integer input only

Implementation note:
- Keep logic thin; interactive mode should call normal command handlers.

---

## Repo Commands

### `suss init`

Initializes a new suss repository.

Actions:
- Create `suss.yaml`
- Create directory skeleton
- Print `.gitignore` suggestion

---

### `suss index`

Rebuilds the derived index.

Actions:
- Scan `specs/testcases/**.md`
- Parse front matter + body
- Validate required fields
- Write `.suss/index.json`

Errors:
- Invalid front matter
- Duplicate IDs

---

## Test Case Commands (`suss tc ...`)

### `suss tc new`

```
suss tc new [INPUT] [-g GROUP]
```

Creates a new test case file.

Behavior:
- If INPUT is omitted, open `$EDITOR` for drafting
- If INPUT is a filepath, import that Markdown as a testcase
- Generate ID/key if not provided

---

### `suss tc show`

```
suss tc show <TC_ID>
```

Outputs raw Markdown to stdout.

---

## List

### `suss list`

```
suss list [-g GROUPS] [-i IDS] [-t TAGS] [--tag-mode any|all] [-s SEARCH] [--search-mode any|all] [--stdout quiet|short|verbose|json] [--limit N]
```

Lists test cases using index.

Notes:
- CSV values are accepted for groups/ids/tags
- Case-insensitive matching by default
- Exact/case-sensitive matching is planned but not yet implemented

Output (short):
- ID | Title | Tags | Group

---

### `suss tc tag add`

```
suss tc tag add <TC_ID> <TAG...>
```

Adds one or more tags.

Implementation:
- Modify YAML front matter
- Update `updated` timestamp

---

### `suss tc tag remove`

```
suss tc tag remove <TC_ID> <TAG...>
```

Removes tags if present.

---

## Suite Commands (`suss suite ...`)

### `suss suite new`

```
suss suite new <SUITE_ID> -t TITLE
```

Creates an empty suite.

---

### `suss suite add`

```
suss suite add <SUITE_ID> <TC_ID...>
```

Appends test cases to suite.

---

### `suss suite remove`

```
suss suite remove <SUITE_ID> <TC_ID...>
```

Removes test cases from suite.

---

### `suss suite show`

```
suss suite show <SUITE_ID>
```

Prints suite contents.

---

### `suss suite list`

```
suss suite list
```

Lists all suites.

---

## Exit Codes

SUSS uses grouped status enums rather than a single numeric table. Each command returns a status code plus a message.

- `UserStatus`: CLI-level outcomes (OK, unexpected, interrupted)
- `ReadStatus`: invalid input/criteria parsing (group/tag/search/output)
- `ParseStatus`: markdown parsing/testcase creation failures
- `WriteStatus`: write/path failures
- `IndexStatus`: index load/duplicate/missing cases
- `ListStatus`: list outcomes (OK/NO_MATCH)

---

## Implementation Notes

- Use `pathlib` exclusively for paths
- Use `yaml` via standard library fallback (manual parser)
- All writes must be atomic (write temp + rename)
- Never modify `.suss/index.json` directly

---

## Guiding Principle

> If a command cannot be explained in one sentence, it is too complex for the MVP.

