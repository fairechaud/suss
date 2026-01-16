# suss CLI – Command Cheatsheet & Implementation Blueprint

This document enumerates **all intended MVP commands**, their purpose, inputs, outputs, and implementation notes.

All commands:
- Use `argparse`
- Support `-h / --help`
- Exit non‑zero on error
- Are safe to script (stdin/stdout, no hidden prompts unless interactive mode)

---

## Global Invocation

```
python suss.py [subcommand] [options]
```

If no subcommand is provided → **interactive mode**.

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
suss tc new [-g GROUP] [-i ID] -t TITLE
```

Creates a new test case file.

Behavior:
- Generate ID if not provided
- Populate front matter template
- Open `$EDITOR` unless `--no-edit`

---

### `suss tc show`

```
suss tc show <TC_ID>
```

Outputs raw Markdown to stdout.

---

### `suss tc list`

```
suss tc list [-g GROUP] [-t TAG] [--search TEXT]
```

Lists test cases using index.

Output:
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

## Markdown Interchange

### `suss tc import`

```
suss tc import [-g GROUP] [--on-collision error|fork]
```

Reads Markdown from stdin and creates test cases.

Behavior:
- Split input into blocks
- Parse front matter or infer
- Assign IDs if missing
- Write files

Collision modes:
- `error`: abort
- `fork`: generate new ID + add `derived_from`

---

### `suss tc export`

```
suss tc export <TC_ID...>
```

Writes one or more test cases to stdout.

Formatting:
- Each test case separated by a deterministic delimiter

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

## Search

### `suss search`

```
suss search <QUERY>
```

Searches across:
- title
- body text
- tags

Implementation options:
- JSON index scan (MVP)
- Optional `ripgrep` fast path

---

## Exit Codes

- `0` success
- `1` user error (invalid args, missing ID)
- `2` repo/config error
- `130` interrupted (Ctrl+C)

---

## Implementation Notes

- Use `pathlib` exclusively for paths
- Use `yaml` via standard library fallback (manual parser)
- All writes must be atomic (write temp + rename)
- Never modify `.suss/index.json` directly

---

## Guiding Principle

> If a command cannot be explained in one sentence, it is too complex for the MVP.

