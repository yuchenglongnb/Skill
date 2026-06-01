"""Conservative text cleanup that preserves evidence placeholders."""

from __future__ import annotations

import re

WHITESPACE = re.compile(r"[ \t\u00a0]+")
BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(value: str) -> str:
    lines = [WHITESPACE.sub(" ", line).strip() for line in value.splitlines()]
    return BLANK_LINES.sub("\n\n", "\n".join(lines)).strip()

