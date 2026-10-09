#!/usr/bin/env python3
"""Test if improved prompt helps model produce correct SEARCH blocks."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.llm import LLMClient
from agent.prompts import build_system_prompt
from agent.repomap.builder import build_repo_map
from agent.patch.parse_blocks import parse_edit_blocks

# Minimal test case
TEST_CODE = '''def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
'''

TASK = "Add a docstring to the add function that says 'Add two numbers and return the result'"

def main():
    # Create temp file
    test_file = Path("temp_test_add.py")
    test_file.write_text(TEST_CODE)
    
    try:
        # Build context
        repo_map = build_repo_map(str(Path.cwd()))
        system_prompt = build_system_prompt(repo_map)
        
        # Show file content to model
        user_message = f"""Here is the current content of {test_file}:

```python
{TEST_CODE}```

Task: {TASK}

**Example of correct format:**
If a file contains:
```python
def hello():
    print("hi")
```

And you want to add a docstring, the SEARCH block must copy EXACTLY what's there now (without the docstring):

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

Now provide the edit blocks to complete the task above."""
        
        print("=" * 80)
        print("SYSTEM PROMPT (excerpt):")
        print("=" * 80)
        print(system_prompt[:800])
        print("...\n")
        
        print("=" * 80)
        print("USER MESSAGE:")
        print("=" * 80)
        print(user_message)
        print()
        
        # Call model
        client = LLMClient(base_url="http://localhost:11434/v1", model="gemma3:4b")
        full_response = ""
        
        print("=" * 80)
        print("MODEL RESPONSE:")
        print("=" * 80)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        for chunk in client.get_completion(messages):
            print(chunk, end="", flush=True)
            full_response += chunk
        print("\n")
        
        # Parse blocks
        print("=" * 80)
        print("PARSED BLOCKS:")
        print("=" * 80)
        blocks = parse_edit_blocks(full_response)
        for i, block in enumerate(blocks, 1):
            print(f"\nBlock {i}:")
            print(f"  Path: {block.path}")
            print(f"  Search block:\n{repr(block.search_block)}")
            print(f"  Replace block:\n{repr(block.replace_block)}")
        
        # Check SEARCH against actual file
        print("\n" + "=" * 80)
        print("VALIDATION:")
        print("=" * 80)
        actual_content = test_file.read_text()
        for i, block in enumerate(blocks, 1):
            if block.search_block in actual_content:
                print(f"✓ Block {i}: SEARCH found exact match in file")
            else:
                print(f"✗ Block {i}: SEARCH not found in file")
                print(f"  Model searched for:\n{block.search_block}")
                print(f"\n  File contains:\n{actual_content}")
                
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    main()
