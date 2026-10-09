import ast
import inspect
from processor import process_items


def test_process_items():
    assert process_items(["hello", "world"]) == ["HELLO", "WORLD"]
    assert process_items(["a", "b", "c"]) == ["A", "B", "C"]


def test_no_unused_imports():
    # Check that unused imports are removed
    source = inspect.getsource(inspect.getmodule(process_items))
    tree = ast.parse(source)
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    # os and sys should be removed, only typing should remain
    assert 'os' not in imports, "Unused import 'os' should be removed"
    assert 'sys' not in imports, "Unused import 'sys' should be removed"
