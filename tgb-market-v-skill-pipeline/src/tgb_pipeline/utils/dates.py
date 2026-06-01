"""Date parsing helpers for Taoguba HTML."""

from __future__ import annotations

import re
from datetime import date, datetime

DATE_PATTERN = re.compile(r"(?P<year>\d{4})[-/.年](?P<month>\d{1,2})[-/.月](?P<day>\d{1,2})日?")
DATETIME_PATTERN = re.compile(
    r"(?P<year>\d{4})[-/.年](?P<month>\d{1,2})[-/.月](?P<day>\d{1,2})日?"
    r"(?:\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})(?::(?P<second>\d{2}))?)?"
)


def parse_date(value: str) -> date:
    match = DATE_PATTERN.search(value)
    if not match:
        raise ValueError(f"could not parse date: {value!r}")
    return date(*(int(match.group(name)) for name in ("year", "month", "day")))


def parse_datetime(value: str) -> datetime:
    match = DATETIME_PATTERN.search(value)
    if not match:
        raise ValueError(f"could not parse datetime: {value!r}")
    values = {
        name: int(match.group(name) or 0)
        for name in ("year", "month", "day", "hour", "minute", "second")
    }
    return datetime(**values)

