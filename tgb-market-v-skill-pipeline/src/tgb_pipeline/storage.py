"""Small JSONL persistence helpers for pipeline entities."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Hashable, Iterable
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class JSONLStore(Generic[ModelT]):
    """Persist one Pydantic model type as append-only JSON Lines records."""

    def __init__(self, path: str | Path, model_type: type[ModelT], key_field: str):
        self.path = Path(path)
        self.model_type = model_type
        self.key_field = key_field
        if key_field not in self._model_fields():
            raise ValueError(f"unknown key field: {key_field}")

    def read_all(self) -> list[ModelT]:
        if not self.path.exists():
            return []

        records: list[ModelT] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(self._parse_json(line))
                except ValueError as exc:
                    raise ValueError(
                        f"invalid JSONL record at {self.path}:{line_number}"
                    ) from exc
        return records

    def append(self, record: ModelT) -> bool:
        return self.append_many([record]) == 1

    def append_many(self, records: Iterable[ModelT]) -> int:
        existing_keys = {
            self._key(record)
            for record in self.read_all()
        }
        new_records: list[ModelT] = []
        for record in records:
            if not isinstance(record, self.model_type):
                raise TypeError(f"expected {self.model_type.__name__}")
            key = self._key(record)
            if key in existing_keys:
                continue
            existing_keys.add(key)
            new_records.append(record)

        if not new_records:
            return 0

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            for record in new_records:
                payload = self._dump_json_compatible(record)
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return len(new_records)

    def rewrite_all(self, records: Iterable[ModelT]) -> int:
        normalized = self._validate_records(records)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8", newline="\n") as handle:
            for record in normalized:
                payload = self._dump_json_compatible(record)
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return len(normalized)

    def upsert_many(self, records: Iterable[ModelT]) -> int:
        existing = {self._key(record): record for record in self.read_all()}
        replacements = 0
        for record in self._validate_records(records):
            if self._key(record) in existing:
                replacements += 1
            existing[self._key(record)] = record
        ordered_records = list(existing.values())
        self.rewrite_all(ordered_records)
        return replacements

    def index_by(self, field_name: str) -> dict[Hashable, list[ModelT]]:
        """Build an in-memory index; list fields contribute one entry per value."""

        if field_name not in self._model_fields():
            raise ValueError(f"unknown index field: {field_name}")

        index: defaultdict[Hashable, list[ModelT]] = defaultdict(list)
        for record in self.read_all():
            value = getattr(record, field_name)
            values = value if isinstance(value, list) else [value]
            for item in values:
                if item is not None:
                    index[self._hashable(item)].append(record)
        return dict(index)

    def _key(self, record: ModelT) -> Hashable:
        return self._hashable(getattr(record, self.key_field))

    def _model_fields(self) -> dict[str, Any]:
        return getattr(self.model_type, "model_fields", None) or self.model_type.__fields__

    def _parse_json(self, line: str) -> ModelT:
        if hasattr(self.model_type, "model_validate_json"):
            return self.model_type.model_validate_json(line)
        return self.model_type.parse_raw(line)

    def _validate_records(self, records: Iterable[ModelT]) -> list[ModelT]:
        normalized: list[ModelT] = []
        seen_keys: set[Hashable] = set()
        for record in records:
            if not isinstance(record, self.model_type):
                raise TypeError(f"expected {self.model_type.__name__}")
            key = self._key(record)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            normalized.append(record)
        return normalized

    @staticmethod
    def _dump_json_compatible(record: ModelT) -> dict[str, Any]:
        if hasattr(record, "model_dump"):
            return record.model_dump(mode="json")
        return json.loads(record.json())

    @staticmethod
    def _hashable(value: Any) -> Hashable:
        if not isinstance(value, Hashable):
            raise TypeError(f"index value is not hashable: {value!r}")
        return value
