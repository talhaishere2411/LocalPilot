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

Rules:
- The path is on its own line, immediately before <<<<<<< SEARCH.
- SEARCH must copy existing lines from the file, including indentation.
- Keep SEARCH as short as possible while matching only one place in the file.
- Edit existing files only. Do not create new files.
- Do not write anything inside a block except file lines.
- When the task is finished, reply with plain text and no edit blocks.
"""


def build_system_prompt(repo_map: str) -> str:
    """Return the system prompt: role, EDIT_FORMAT_INSTRUCTIONS, and `repo_map`."""
    return f"""\
You are a coding assistant that edits files safely using SEARCH/REPLACE blocks.

{EDIT_FORMAT_INSTRUCTIONS}

Repository overview:
{repo_map}
"""
