#!/usr/bin/env python3
"""ソースコードの構造インベントリを取得する。

Usage:
    python inventory_source.py <path> [--json out.json]

対象ディレクトリを走査し、言語別ファイル一覧・行数、
Python ファイルのクラス/関数/docstring を抽出する。
"""
import argparse
import ast
import json
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
    "build", ".idea", ".vscode", "target", "coverage", ".next",
}
EXT_TO_LANG = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".jsx": "JavaScript", ".java": "Java",
    ".go": "Go", ".rs": "Rust", ".c": "C", ".h": "C", ".cpp": "C++",
    ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
    ".kt": "Kotlin", ".scala": "Scala", ".sh": "Shell", ".sql": "SQL",
    ".html": "HTML", ".css": "CSS", ".vue": "Vue",
}


def count_lines(path: Path) -> int:
    try:
        return sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore"))
    except OSError:
        return -1


def parse_python(path: Path) -> dict:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (SyntaxError, OSError):
        return {"classes": [], "functions": []}
    classes, functions = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            classes.append({"name": node.name, "line": node.lineno,
                            "doc": (doc or "")[:200]})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node)
            args = [a.arg for a in node.args.args]
            functions.append({"name": node.name, "line": node.lineno,
                              "args": args, "doc": (doc or "")[:200]})
    return {"classes": classes, "functions": functions}


def inventory(root: Path) -> dict:
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        rel = str(p.relative_to(root))
        lang = EXT_TO_LANG.get(p.suffix.lower(), "Other")
        entry = {"path": rel, "lang": lang, "lines": count_lines(p)}
        if lang == "Python" and p.suffix == ".py":
            entry.update(parse_python(p))
        files.append(entry)

    by_lang = {}
    for f in files:
        d = by_lang.setdefault(f["lang"], {"files": 0, "lines": 0})
        d["files"] += 1
        d["lines"] += max(f["lines"], 0)
    return {"root": str(root), "total_files": len(files), "by_lang": by_lang, "files": files}


def main() -> None:
    ap = argparse.ArgumentParser(description="ソースコードインベントリ")
    ap.add_argument("path", help="対象ファイルまたはディレクトリ")
    ap.add_argument("--json", dest="out", help="JSON 出力先(省略時は stdout に要約)")
    args = ap.parse_args()
    root = Path(args.path)
    if not root.exists():
        sys.exit(f"not found: {root}")
    if root.is_file():
        root = root.parent
        print(f"note: file given; scanning parent directory {root}", file=sys.stderr)
    data = inventory(root)
    if args.out:
        Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(f"root: {data['root']}  files: {data['total_files']}")
        for lang, d in sorted(data["by_lang"].items(), key=lambda x: -x[1]["lines"]):
            print(f"  {lang}: {d['files']} files, {d['lines']} lines")


if __name__ == "__main__":
    main()
