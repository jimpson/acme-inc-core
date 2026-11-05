#!/usr/bin/env python3
"""Diff-aware convention gate for acme-inc-core.

Gates changes under `wrapper/`. "Changed" means any wrapper/*.py that differs from
the base ref OR is staged, unstaged, or untracked in the working tree - so a new
file the agent just wrote is checked even before it is committed. For each such
file three checks run:

  1. deprecated-api : no deprecated scikit-image calls (all matches reported)
  2. boundary       : import roots limited to the whitelist; no private skimage
                      (`skimage._*` or underscored imported names); no
                      third-party libraries outside the allowlist
  3. weak-tests     : tests/test_<name>.py exists, references the module under
                      test, and makes at least one non-trivial assertion
                      (`assert True` / constant assertions do not count)

If every changed file passes, the full pytest suite must pass too, unless
--no-tests is given (static checks only - used by the in-editor Cursor hook).

Scope notes for authors:
  * Only wrapper/ is scanned. core/ is never gated.
  * deprecated-api is a regex over raw source, so a match inside a comment or
    docstring still trips it; keep deprecated tokens out of prose too.
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


def _git(args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).splitlines()
    except subprocess.CalledProcessError:
        return []


def _keep(path_str):
    p = path_str.strip()
    return (
        p.startswith("wrapper/")
        and p.endswith(".py")
        and not p.endswith("__init__.py")
    )


def changed_wrapper_files(base: str) -> list[pathlib.Path]:
    names = set()
    committed = _git(["diff", "--name-only", f"{base}...HEAD"]) or _git(
        ["diff", "--name-only", base]
    )
    names.update(committed)
    names.update(_git(["diff", "--name-only", "--cached"]))
    names.update(_git(["diff", "--name-only"]))
    names.update(_git(["ls-files", "--others", "--exclude-standard"]))

    files = {}
    for n in names:
        if _keep(n):
            fp = ROOT / n.strip()
            if fp.exists():
                files[str(fp)] = fp
    return [files[k] for k in sorted(files)]


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
    ap.add_argument("--no-tests", action="store_true",
                    help="static checks only; skip pytest (used by the in-editor hook)")
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

    if args.no_tests:
        print("\nconvention gate passed (static checks only).")
        sys.exit(0)

    print("\nconvention gate passed; running tests...")
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=ROOT))


if __name__ == "__main__":
    main()
