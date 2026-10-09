---
name: safe-edit
description: Propose a code edit as a SEARCH/REPLACE block so a verification harness can validate it before anything is written to disk. Use when modifying existing source files.
---

# safe-edit

Propose every file change as one or more SEARCH/REPLACE blocks. Never write to a file directly; the harness validates each block (path, patch match, syntax, lint and tests) before it is applied.

## Block format (locked)

```
path/relative/to/project/root.py
<<<<<<< SEARCH
exact existing lines to replace
=======
new lines
>>>>>>> REPLACE
```

## Rules

1. The path is on its own line, immediately before `<<<<<<< SEARCH`, relative to the project root.
2. `SEARCH` copies existing lines from the file, including indentation.
3. Keep `SEARCH` as short as possible while matching exactly one place in the file.
4. Edit existing files only. Creating new files is out of scope for version 1.
5. A reply may contain several blocks. They are applied in order.
6. The parser tolerates blocks wrapped in a Markdown code fence and trailing whitespace on marker lines.
7. When the task is complete, reply in plain text with no blocks.

## Example

```
src/utils.py
<<<<<<< SEARCH
def calculate_total(items):
    return sum(items)
=======
def calculate_total(items, discount_rate=0.0):
    return sum(items) * (1 - discount_rate)
>>>>>>> REPLACE
```
