# test-pilot

Parse a Python file's AST and emit a pytest-shaped skeleton for what it finds.

~93 lines, no dependencies, stdlib `ast` only. It is a scaffolding starting
point, not a test generator that produces passing tests.

## Real output

Given `calculator.py` with `add(a, b)`, `greet(name, greeting="hello")`, and a
`Point` class with `__init__`, `norm`, `scale`:

```
$ test-pilot calculator.py -o test_calc.py
✓ 生成了 5 个测试
   输出: test_calc.py

$ cat test_calc.py
# Auto-generated tests for calculator.py
# Source: calculator.py
import sys; sys.path.insert(0, '.')

import calculator

def test_add():
    """Auto-generated test for add"""
    result = calculator.add(..., ...)
    assert result is not None  # TODO: add assertions


def test_greet():
    """Auto-generated test for greet"""
    result = calculator.greet(..., ...)
    assert result is not None  # TODO: add assertions


# Tests for Point

def test_Point___init__():
    """Auto-generated test for Point.__init__"""
    result = calculator.Point().__init__(..., ..., ...)
    assert result is not None  # TODO: add assertions


def test_Point_norm():
    """Auto-generated test for Point.norm"""
    result = calculator.Point().norm(...)
    assert result is not None  # TODO: add assertions


def test_Point_scale():
    """Auto-generated test for Point.scale"""
    result = calculator.Point().scale(..., ...)
    assert result is not None  # TODO: add assertions
```

The ellipses are literal in the output — one per positional parameter, with no
values filled in.

## Install

```bash
pip install -e .
```

Requires Python 3.10+ (uses `ast`). Installs the `test-pilot` console script.

## Usage

```bash
test-pilot <file.py> [-o OUTPUT]
```

`file.py` must end in `.py`, otherwise it prints `只支持 .py 文件` and exits 1.
`-o` is effectively required (see below); the generated file is only written when
`-o` is given.

It prints the count of generated `def test_` lines and the output path.

中文说明：读取 Python 源码的 AST，为顶层函数和类方法生成 pytest 测试骨架。
生成结果里的参数是 `...` 占位符，需要你自己填值和断言。

## What it actually inspects

`ast.iter_child_nodes(tree)` — **top-level definitions only**. It records:

- module-level `FunctionDef` nodes and their positional arg names
- module-level `ClassDef` nodes and their direct `FunctionDef` methods

The recorded arg names are never used in the output; only their *count* is.

## What this is not

- **The generated tests do not pass.** Every parameter is `...`, so
  `calculator.add(..., ...)` raises `TypeError: unsupported operand type(s) for
  '+': 'ellipsis' and 'ellipsis'`. The output is a template you fill in, not a
  regression suite. Do not put it in CI as-is.
- **No boundary values.** The `pyproject.toml` description claims 边界值
  (edge cases); there is no value-generation code anywhere in the package. The
  only assertion emitted is `assert result is not None`.
- **Nothing is inferred.** No fixtures, no mocks, no type-directed values, no
  import analysis, no coverage of decorators, `async def`, `*args`/`**kwargs`,
  or default values. Positional args are counted; keyword-only and defaults are
  ignored.
- **`-o` is de facto mandatory.** Without it, `cli.py` raises
  `UnboundLocalError: cannot access local variable 'Path'` — `Path` is imported
  *after* the line that uses it. The `--output` help text claims a default of
  `test_<filename>`; that path is unreachable.
- **Nested functions and methods of nested classes are skipped**, as is anything
  behind a conditional — `ast.iter_child_nodes` on the module body only.
- **The generated file is not valid standalone.** It does `import <module>` by
  stem, which only resolves if the source dir is on `sys.path` and you run from
  the right cwd.
- No tests, no config, no library API (`__init__.py` is empty; `generate_tests`
  is importable but undocumented).

## Requirements

Python 3.10+. No dependencies. pytest is not imported or required to generate.

## License

MIT