#!/usr/bin/env python3
"""Diff-aware convention gate for acme-inc-core.

Only changes under `wrapper/` are gated. For each changed `wrapper/*.py` file
(compared to a base ref) three checks run:

  1. deprecated-api : no deprecated scikit-image calls
  2. boundary       : imports limited to the whitelist (no private skimage, no
                      third-party libraries outside the allowlist)
  3. weak-tests     : each changed wrapper module has tests/test_<name>.py with
                      at least one assertion

If all changed files pass, the full test suite must pass too.
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
    for pat in DEPRECATED:
        m = re.search(pat, src)
        if m:
            fails.append(("deprecated-api", _rel(path),
                          f"deprecated scikit-image usage: {m.group(0)!r}"))
            return


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


def check_tests(path, fails):
    name = path.stem
    test = ROOT / "tests" / f"test_{name}.py"
    if not test.exists():
        fails.append(("weak-tests", _rel(path), f"missing tests/test_{name}.py"))
        return
    ttree = ast.parse(test.read_text())
    if not any(isinstance(n, ast.Assert) for n in ast.walk(ttree)):
        fails.append(("weak-tests", _rel(path),
                      f"tests/test_{name}.py has no assertions (weak test)"))


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
