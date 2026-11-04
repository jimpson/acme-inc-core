#!/usr/bin/env python3
"""Diff-aware convention gate for acme-inc-core.

Only changes under `wrapper/` are gated. For each changed `wrapper/*.py` file
(compared to a base ref) three checks run against that files diff:

  1. deprecated-api : no deprecated scikit-image calls (all matches reported)
  2. boundary       : import roots limited to the whitelist; no private skimage
                      (`skimage._*` or underscored imported names); no
                      third-party libraries outside the allowlist
  3. weak-tests     : tests/test_<name>.py exists, references the module under
                      test, and makes at least one non-trivial assertion
                      (a bare/constant assertion such as `assert True` does not
                      count)

If every changed file passes, the full pytest suite must pass too.

Scope notes for authors:
  * Checks run only on the *diff* under `wrapper/`. `core/` is never scanned.
  * deprecated-api is a regex over raw source, so a match inside a comment or
    docstring will still trip it; keep deprecated tokens out of prose too.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

DEPRECATED = [
    r"\bmultichannel\s*=",
    r"\brgb2grey\b",
    r"\bselem\s*=",
    r"\butil\.pad\b",
    r"\bmarching_cubes_lewiner\b",
    r"\bcompare_ssim\b",
    r"\bcompare_psnr\b",
]

ALLOWED_ROOTS = {
    "core", "wrapper", "skimage", "numpy", "np",
    "math", "typing", "dataclasses", "functools", "itertools",
    "collections", "statistics", "__future__",
}


def changed_wrapper_files(base: str) -> list[pathlib.Path]:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", f"{base}...HEAD"], cwd=ROOT, text=True
        )
    except subprocess.CalledProcessError:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", base], cwd=ROOT, text=True
        )
    files = []
    for line in out.splitlines():
        p = line.strip()
        if p.startswith("wrapper/") and p.endswith(".py") and not p.endswith("__init__.py"):
            fp = ROOT / p
            if fp.exists():
                files.append(fp)
    return files


def check_deprecated(path, src, fails):
    seen = set()
    for pat in DEPRECATED:
        for m in re.finditer(pat, src):
            token = m.group(0)
            if token in seen:
                continue
            seen.add(token)
            fails.append(("deprecated-api", _rel(path),
                          f"deprecated scikit-image usage: {token!r}"))


def check_imports(path, tree, fails):
    def root(name):
        return name.split(".")[0]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if root(a.name) not in ALLOWED_ROOTS:
                    fails.append(("boundary", _rel(path), f"import outside whitelist: {a.name}"))
                if a.name.startswith("skimage") and "._" in a.name:
                    fails.append(("boundary", _rel(path), f"private skimage import: {a.name}"))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod and root(mod) not in ALLOWED_ROOTS:
                fails.append(("boundary", _rel(path), f"import outside whitelist: {mod}"))
            private = mod.startswith("skimage") and (
                "._" in mod or any(n.name.startswith("_") for n in node.names)
            )
            if private:
                fails.append(("boundary", _rel(path), f"private skimage import: {mod}"))


def _is_nontrivial_assert(assert_node) -> bool:
    # A meaningful assertion references a value: a call, attribute access,
    # subscript, or name. `assert True`, `assert 1`, `assert 1 == 2` are all
    # constant-only and do not count.
    for n in ast.walk(assert_node.test):
        if isinstance(n, (ast.Call, ast.Attribute, ast.Subscript, ast.Name)):
            return True
    return False


def check_tests(path, fails):
    name = path.stem
    test = ROOT / "tests" / f"test_{name}.py"
    if not test.exists():
        fails.append(("weak-tests", _rel(path), f"missing tests/test_{name}.py"))
        return
    test_src = test.read_text()
    try:
        ttree = ast.parse(test_src)
    except SyntaxError as e:
        fails.append(("weak-tests", _rel(path), f"test file does not parse: {e}"))
        return

    asserts = [n for n in ast.walk(ttree) if isinstance(n, ast.Assert)]
    if not asserts:
        fails.append(("weak-tests", _rel(path),
                      f"tests/test_{name}.py has no assertions (weak test)"))
        return
    if not any(_is_nontrivial_assert(a) for a in asserts):
        fails.append(("weak-tests", _rel(path),
                      f"tests/test_{name}.py has only trivial/constant assertions (weak test)"))
        return
    if not re.search(rf"\b{re.escape(name)}\b", test_src):
        fails.append(("weak-tests", _rel(path),
                      f"tests/test_{name}.py does not exercise wrapper.{name}"))


def _rel(path):
    return str(path.relative_to(ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    args = ap.parse_args()

    files = changed_wrapper_files(args.base)
    print(f"gate: {len(files)} changed wrapper file(s) vs {args.base}")
    for f in files:
        print(f"  - {_rel(f)}")

    fails = []
    for f in files:
        src = f.read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            fails.append(("boundary", _rel(f), f"syntax error: {e}"))
            continue
        check_deprecated(f, src, fails)
        check_imports(f, tree, fails)
        check_tests(f, fails)

    if fails:
        print("\nCONVENTION GATE FAILED:")
        for cat, where, msg in fails:
            print(f"  [{cat}] {where}: {msg}")
        sys.exit(1)

    print("\nconvention gate passed; running tests...")
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=ROOT))


if __name__ == "__main__":
    main()
