#!/usr/bin/env python3
"""Check TeX prose sentence-per-line conventions in the manuscript."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT_FILE = ROOT / 'docs' / 'writing' / 'manuscript' / 'main.tex'

env_start_re = re.compile(r'\\begin\{([^}]+)\}')
env_end_re = re.compile(r'\\end\{([^}]+)\}')
command_only_re = re.compile(r'^\s*\\[A-Za-z@]+(?:\[[^\]]*\])?(?:\{[^}]*\})*\s*$')
sentence_sep_re = re.compile(r'[。.!?！？]')
path_command_re = re.compile(
    r'^\s*\\(?:graphicspath|includegraphics|input|include|bibliography)\b'
)

IGNORE_ENV_NAMES = {
    'equation', 'equation*', 'align', 'align*', 'alignat', 'alignat*',
    'eqnarray', 'eqnarray*', 'gather', 'gather*',
    'table', 'table*', 'tabular', 'tabular*',
    'figure', 'figure*', 'subfigure',
    'tikzpicture', 'pgfplots',
    'lstlisting', 'verbatim', 'minted', 'algorithm', 'algorithmic',
    'math', 'displaymath'
}


def is_command_only(line: str) -> bool:
    return bool(command_only_re.match(line) or path_command_re.match(line))


def is_invalid_sentence_line(line: str) -> bool:
    if is_command_only(line):
        return False
    return len(sentence_sep_re.findall(line)) > 1


def scan_file(path: Path, issues: list[str]) -> None:
    env_depth = 0
    for idx, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue

        if line.startswith('%'):
            continue

        begin = env_start_re.search(line)
        if begin and begin.group(1) in IGNORE_ENV_NAMES:
            env_depth += 1
            continue

        if env_depth > 0:
            end = env_end_re.search(line)
            if end and end.group(1) in IGNORE_ENV_NAMES:
                env_depth = max(env_depth - 1, 0)
            continue

        end = env_end_re.search(line)
        if end and end.group(1) in IGNORE_ENV_NAMES:
            continue

        if is_invalid_sentence_line(line):
            issues.append(f"{path}:{idx}: multiple sentence-ending marks in one prose line")


def main() -> int:
    issues: list[str] = []
    if not MANUSCRIPT_FILE.exists():
        print(f"No manuscript file: {MANUSCRIPT_FILE}")
        return 0

    scan_file(MANUSCRIPT_FILE, issues)

    if issues:
        print('Sentence-line check failed:')
        for item in issues:
            print(item)
        print(f'Found {len(issues)} issue(s).')
        return 1

    print('Sentence-line style check passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
