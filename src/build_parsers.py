"""Verify tree-sitter Python parser.

Owner: Developer A (task A1). tree-sitter-language-pack ships prebuilt
grammars, so this script only verifies the parser works.
"""

import sys
from pathlib import Path

# Ensure agent module is importable
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))

from agent.parsing import count_error_nodes, get_python_parser


def main() -> None:
    parser = get_python_parser()
    test_code = "x = 1\n"
    tree = parser.parse(test_code.encode("utf-8"))
    
    assert tree.root_node is not None, "Parser failed to parse test code"
    assert count_error_nodes(test_code) == 0, "Valid code has errors"
    
    print("tree-sitter Python parser OK")


if __name__ == "__main__":
    main()
