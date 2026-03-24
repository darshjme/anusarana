"""Span — a single traced operation."""

from __future__ import annotations

import time
import uuid
from typing import Any


class Span:
    """Represents a single traced operation in an agent call graph."""

    def __init__(
        self,
        name: str,
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.span_id: str = str(uuid.uuid4())
        self.name: str = name
        self.parent_id: str | None = parent_id
        self.metadata: dict[str, Any] = metadata or {}
        self.start_time: float = time.time()
        self.end_time: float | None = None
        self.status: str = "active"
        self.error: str | None = None

    def finish(self, error: str | None = None) -> None:
        """Mark this span as complete. Sets status to 'error' or 'success'."""
        self.end_time = time.time()
        if error is not None:
            self.status = "error"
            self.error = error
        else:
            self.status = "success"

    @property
    def duration_ms(self) -> float | None:
        """Duration in milliseconds, or None if still active."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize span to a dictionary."""
        return {
            "span_id": self.span_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }

    def __repr__(self) -> str:
        return (
            f"Span(name={self.name!r}, status={self.status!r}, "
            f"span_id={self.span_id!r})"
        )
