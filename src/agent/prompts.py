"""Prompt text sent to the model.

Owner: Developer B.
"""

EDIT_FORMAT_INSTRUCTIONS = """\
To change a file, reply with one or more edit blocks in exactly this format:

path/relative/to/project/root.py
<<<<<<< SEARCH
exact existing lines to replace
=======
new lines
>>>>>>> REPLACE

CRITICAL RULES FOR SEARCH BLOCKS:
- SEARCH must contain EXACT text from the file - character-for-character match
- Copy the lines EXACTLY as they appear, preserving all spacing and indentation
- Do NOT add comments, docstrings, or any text that isn't already there
- Do NOT remove or modify existing content in the SEARCH block
- If a function has no docstring, do NOT add one in SEARCH
- The SEARCH block is for finding existing code, not showing what you wish it said

Other rules:
- The path is on its own line, immediately before <<<<<<< SEARCH
- Keep SEARCH as short as possible while matching only one place in the file
- Edit existing files only. Do not create new files
- Do not write anything inside a block except file lines
- When the task is finished, reply with plain text and no edit blocks
"""

FEW_SHOT_EXAMPLE = """\
**Example of correct format:**

If you want to add a docstring to a function that currently has none, the SEARCH block must copy the code EXACTLY as it exists now (without the docstring):

```
example.py
<<<<<<< SEARCH
def hello():
    print("hi")
=======
def hello():
    \"\"\"Say hello.\"\"\"
    print("hi")
>>>>>>> REPLACE
```

The SEARCH block shows what's there NOW, the REPLACE block shows what it should become."""


def build_system_prompt(repo_map: str) -> str:
    """Return the system prompt: role, EDIT_FORMAT_INSTRUCTIONS, and `repo_map`."""
    return f"""\
You are a coding assistant that edits files safely using SEARCH/REPLACE blocks.

{EDIT_FORMAT_INSTRUCTIONS}

Repository overview:
{repo_map}
"""


def build_task_message(task: str) -> str:
    """Build the initial task message with few-shot example."""
    return f"""{FEW_SHOT_EXAMPLE}

{task}"""
