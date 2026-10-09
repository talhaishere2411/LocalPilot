# Benchmark task format

Each task is one folder under `bench/tasks/`:

```
bench/tasks/<task_id>/
├── task.json
└── project/          a tiny Python project (2-3 files), ideally with pytest tests
```

`task.json`:

```json
{
  "id": "add_docstring",
  "description": "Add a docstring to the main function in main.py.",
  "success_cmd": "python -m pytest -q"
}
```

- `description` is the exact text given to the agent as the task.
- `success_cmd` is run inside a fresh temporary copy of `project/` after the agent finishes. Exit code 0 means the task succeeded.

Target: 10-15 tasks.
