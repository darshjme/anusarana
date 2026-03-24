"""Comprehensive pytest tests for agent-tracer — 30+ tests."""

from __future__ import annotations

import asyncio
import time
import uuid

import pytest

from agent_tracer import Span, Tracer, trace_call


# ─────────────────────────── Span tests ────────────────────────────


class TestSpanInit:
    def test_span_has_uuid_span_id(self):
        s = Span("op")
        uuid.UUID(s.span_id)  # must not raise

    def test_span_name_stored(self):
        s = Span("my_op")
        assert s.name == "my_op"

    def test_span_default_parent_is_none(self):
        s = Span("op")
        assert s.parent_id is None

    def test_span_parent_id_stored(self):
        s = Span("op", parent_id="abc-123")
        assert s.parent_id == "abc-123"

    def test_span_metadata_stored(self):
        meta = {"key": "value", "n": 42}
        s = Span("op", metadata=meta)
        assert s.metadata == meta

    def test_span_default_metadata_is_empty_dict(self):
        s = Span("op")
        assert s.metadata == {}

    def test_span_initial_status_is_active(self):
        s = Span("op")
        assert s.status == "active"

    def test_span_initial_end_time_is_none(self):
        s = Span("op")
        assert s.end_time is None

    def test_span_initial_error_is_none(self):
        s = Span("op")
        assert s.error is None

    def test_span_start_time_is_float(self):
        s = Span("op")
        assert isinstance(s.start_time, float)
        assert s.start_time > 0


class TestSpanFinish:
    def test_finish_sets_end_time(self):
        s = Span("op")
        s.finish()
        assert s.end_time is not None

    def test_finish_without_error_sets_success(self):
        s = Span("op")
        s.finish()
        assert s.status == "success"

    def test_finish_with_error_sets_error_status(self):
        s = Span("op")
        s.finish(error="something went wrong")
        assert s.status == "error"

    def test_finish_with_error_stores_error_message(self):
        s = Span("op")
        s.finish(error="timeout")
        assert s.error == "timeout"

    def test_finish_without_error_leaves_error_none(self):
        s = Span("op")
        s.finish()
        assert s.error is None

    def test_duration_ms_is_none_while_active(self):
        s = Span("op")
        assert s.duration_ms is None

    def test_duration_ms_after_finish(self):
        s = Span("op")
        time.sleep(0.01)
        s.finish()
        assert s.duration_ms is not None
        assert s.duration_ms >= 0

    def test_duration_ms_is_positive(self):
        s = Span("op")
        time.sleep(0.005)
        s.finish()
        assert s.duration_ms > 0


class TestSpanToDict:
    def test_to_dict_contains_all_keys(self):
        s = Span("op")
        s.finish()
        d = s.to_dict()
        expected = {
            "span_id", "name", "parent_id", "metadata",
            "start_time", "end_time", "status", "error", "duration_ms",
        }
        assert expected.issubset(d.keys())

    def test_to_dict_values_match(self):
        meta = {"tool": "search"}
        s = Span("call_tool", parent_id="parent-1", metadata=meta)
        s.finish()
        d = s.to_dict()
        assert d["name"] == "call_tool"
        assert d["parent_id"] == "parent-1"
        assert d["metadata"] == meta
        assert d["status"] == "success"

    def test_to_dict_error_field(self):
        s = Span("op")
        s.finish(error="API failure")
        d = s.to_dict()
        assert d["error"] == "API failure"
        assert d["status"] == "error"


# ─────────────────────────── Tracer tests ──────────────────────────


class TestTracerInit:
    def test_tracer_default_trace_id_is_uuid(self):
        t = Tracer()
        uuid.UUID(t.trace_id)  # must not raise

    def test_tracer_custom_trace_id(self):
        t = Tracer(trace_id="custom-id-123")
        assert t.trace_id == "custom-id-123"

    def test_tracer_starts_empty(self):
        t = Tracer()
        assert t.spans == []


class TestTracerSpans:
    def test_start_span_returns_span(self):
        t = Tracer()
        s = t.start_span("op")
        assert isinstance(s, Span)

    def test_start_span_is_registered(self):
        t = Tracer()
        s = t.start_span("op")
        assert s in t.spans

    def test_finish_span_by_id(self):
        t = Tracer()
        s = t.start_span("op")
        t.finish_span(s.span_id)
        assert s.status == "success"

    def test_finish_span_with_error(self):
        t = Tracer()
        s = t.start_span("op")
        t.finish_span(s.span_id, error="crash")
        assert s.status == "error"
        assert s.error == "crash"

    def test_finish_span_unknown_id_is_noop(self):
        t = Tracer()
        t.finish_span("nonexistent-id")  # must not raise

    def test_get_span_found(self):
        t = Tracer()
        s = t.start_span("op")
        assert t.get_span(s.span_id) is s

    def test_get_span_not_found_returns_none(self):
        t = Tracer()
        assert t.get_span("nope") is None

    def test_root_spans_no_parent(self):
        t = Tracer()
        root = t.start_span("root")
        child = t.start_span("child", parent_id=root.span_id)
        assert root in t.root_spans
        assert child not in t.root_spans

    def test_children_of(self):
        t = Tracer()
        root = t.start_span("root")
        child1 = t.start_span("child1", parent_id=root.span_id)
        child2 = t.start_span("child2", parent_id=root.span_id)
        children = t.children_of(root.span_id)
        assert child1 in children
        assert child2 in children
        assert root not in children

    def test_children_of_no_children(self):
        t = Tracer()
        s = t.start_span("lone")
        assert t.children_of(s.span_id) == []

    def test_to_dict_structure(self):
        t = Tracer(trace_id="trace-1")
        root = t.start_span("agent")
        child = t.start_span("tool_call", parent_id=root.span_id)
        root.finish()
        child.finish()
        d = t.to_dict()
        assert d["trace_id"] == "trace-1"
        assert d["total_spans"] == 2
        root_entries = d["spans"]
        assert len(root_entries) == 1
        assert root_entries[0]["name"] == "agent"
        assert len(root_entries[0]["children"]) == 1
        assert root_entries[0]["children"][0]["name"] == "tool_call"

    def test_to_dict_deeply_nested(self):
        t = Tracer()
        a = t.start_span("A")
        b = t.start_span("B", parent_id=a.span_id)
        c = t.start_span("C", parent_id=b.span_id)
        for span in [a, b, c]:
            span.finish()
        d = t.to_dict()
        assert d["spans"][0]["children"][0]["children"][0]["name"] == "C"


# ─────────────────────────── Decorator tests ────────────────────────


class TestTraceCallDecorator:
    def test_decorator_creates_span(self):
        t = Tracer()

        @trace_call(t, name="my_func")
        def my_func():
            return 42

        my_func()
        assert len(t.spans) == 1
        assert t.spans[0].name == "my_func"

    def test_decorator_finishes_span_on_success(self):
        t = Tracer()

        @trace_call(t)
        def my_func():
            return "ok"

        my_func()
        assert t.spans[0].status == "success"

    def test_decorator_uses_function_qualname_as_default_name(self):
        t = Tracer()

        @trace_call(t)
        def named_fn():
            pass

        named_fn()
        # qualname includes enclosing scope (e.g. "TestClass.<locals>.named_fn")
        assert "named_fn" in t.spans[0].name

    def test_decorator_injects_span_id_if_accepted(self):
        t = Tracer()
        received = {}

        @trace_call(t, name="injected")
        def fn(span_id=None):
            received["span_id"] = span_id

        fn()
        assert received["span_id"] is not None
        assert received["span_id"] == t.spans[0].span_id

    def test_decorator_does_not_inject_span_id_if_not_accepted(self):
        t = Tracer()

        @trace_call(t, name="no_inject")
        def fn(x):
            return x * 2

        result = fn(5)
        assert result == 10

    def test_decorator_sets_error_on_exception(self):
        t = Tracer()

        @trace_call(t, name="boom")
        def boom():
            raise ValueError("exploded")

        with pytest.raises(ValueError):
            boom()

        assert t.spans[0].status == "error"
        assert "exploded" in t.spans[0].error

    def test_decorator_reraises_exception(self):
        t = Tracer()

        @trace_call(t)
        def fail():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError, match="fail"):
            fail()

    def test_decorator_with_parent_id(self):
        t = Tracer()
        root = t.start_span("root")

        @trace_call(t, name="child_op", parent_id=root.span_id)
        def child_op():
            return "done"

        child_op()
        assert t.spans[1].parent_id == root.span_id

    def test_decorator_async_function(self):
        t = Tracer()

        @trace_call(t, name="async_op")
        async def async_op():
            await asyncio.sleep(0)
            return "async_done"

        result = asyncio.run(async_op())
        assert result == "async_done"
        assert t.spans[0].status == "success"

    def test_decorator_async_exception(self):
        t = Tracer()

        @trace_call(t, name="async_fail")
        async def async_fail():
            raise ValueError("async error")

        with pytest.raises(ValueError):
            asyncio.run(async_fail())

        assert t.spans[0].status == "error"
        assert "async error" in t.spans[0].error
