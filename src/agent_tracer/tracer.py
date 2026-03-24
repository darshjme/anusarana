"""Tracer — manages a trace tree of Spans."""

from __future__ import annotations

import uuid
from typing import Any

from .span import Span


class Tracer:
    """Manages a collection of spans forming a trace tree."""

    def __init__(self, trace_id: str | None = None) -> None:
        self.trace_id: str = trace_id or str(uuid.uuid4())
        self._spans: dict[str, Span] = {}

    def start_span(
        self,
        name: str,
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Span:
        """Create and register a new span."""
        span = Span(name=name, parent_id=parent_id, metadata=metadata)
        self._spans[span.span_id] = span
        return span

    def finish_span(self, span_id: str, error: str | None = None) -> None:
        """Finish a span by ID. No-op if span not found."""
        span = self._spans.get(span_id)
        if span is not None:
            span.finish(error=error)

    def get_span(self, span_id: str) -> Span | None:
        """Retrieve a span by ID."""
        return self._spans.get(span_id)

    @property
    def spans(self) -> list[Span]:
        """All spans in insertion order."""
        return list(self._spans.values())

    @property
    def root_spans(self) -> list[Span]:
        """Spans with no parent."""
        return [s for s in self._spans.values() if s.parent_id is None]

    def children_of(self, span_id: str) -> list[Span]:
        """Return direct children of the given span."""
        return [s for s in self._spans.values() if s.parent_id == span_id]

    def _span_to_nested(self, span: Span) -> dict[str, Any]:
        d = span.to_dict()
        d["children"] = [
            self._span_to_nested(child) for child in self.children_of(span.span_id)
        ]
        return d

    def to_dict(self) -> dict[str, Any]:
        """Full trace as nested dict (roots with children embedded)."""
        return {
            "trace_id": self.trace_id,
            "spans": [self._span_to_nested(s) for s in self.root_spans],
            "total_spans": len(self._spans),
        }

    def __repr__(self) -> str:
        return f"Tracer(trace_id={self.trace_id!r}, spans={len(self._spans)})"
