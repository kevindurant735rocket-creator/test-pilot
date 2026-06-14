"""Test generator using AST analysis."""
import ast, os, sys
from pathlib import Path

FUNC_TEMPLATE = '''
def test_{name}():
    """Auto-generated test for {orig_name}"""
    result = {call}
    assert result is not None  # TODO: add assertions
'''

CLASS_TEMPLATE = '''
class Test{name}:
    """Tests for {orig_name}"""
    def test_{method}(self):
        result = {call}
        assert result is not None
'''

def analyze_file(filepath: str) -> list[dict]:
    with open(filepath) as f:
        tree = ast.parse(f.read())
    tests = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            call = f"{node.name}({', '.join(['...'] * len(args))})"
            tests.append({
                "type": "function",
                "name": node.name,
                "args": args,
                "call": call,
            })
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [a.arg for a in item.args.args]
                    methods.append({
                        "name": item.name,
                        "args": args,
                        "call": f"{node.name}().{item.name}({', '.join(['...'] * len(args))})",
                    })
            tests.append({"type": "class", "name": node.name, "methods": methods})
    return tests

def generate_tests(filepath: str, output: str = None) -> str:
    tests = analyze_file(filepath)
    if not tests:
        return "# No callable definitions found\n"
    
    lines = [f"# Auto-generated tests for {os.path.basename(filepath)}", 
             f"# Source: {filepath}", "import sys; sys.path.insert(0, '.')", ""]
    
    module_name = Path(filepath).stem
    lines.append(f"import {module_name}")
    
    for t in tests:
        if t["type"] == "function":
            lines.append(FUNC_TEMPLATE.format(
                name=t["name"], orig_name=t["name"],
                call=f"{module_name}.{t['call']}"
            ))
        elif t["type"] == "class":
            lines.append(f"\n# Tests for {t['name']}")
            for m in t["methods"]:
                lines.append(FUNC_TEMPLATE.format(
                    name=f"{t['name']}_{m['name']}",
                    orig_name=f"{t['name']}.{m['name']}",
                    call=f"{module_name}.{m['call']}"
                ))
    
    result = "\n".join(lines)
    if output:
        Path(output).write_text(result)
    return result
