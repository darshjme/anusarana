"""@trace_call decorator — wraps a function with span tracing."""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable

from .tracer import Tracer


def trace_call(
    tracer: Tracer,
    name: str | None = None,
    parent_id: str | None = None,
) -> Callable:
    """
    Decorator factory that traces a function call as a Span.

    Usage:
        @trace_call(tracer, name="fetch_data", parent_id=root_span.span_id)
        def fetch_data(url: str, span_id: str = None):
            ...

    If the wrapped function accepts a `span_id` keyword argument, the
    active span's ID is injected automatically.
    """
    def decorator(fn: Callable) -> Callable:
        span_name = name or fn.__qualname__

        # Detect if the function accepts span_id
        sig = inspect.signature(fn)
        accepts_span_id = "span_id" in sig.parameters

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = tracer.start_span(
                name=span_name,
                parent_id=parent_id,
                metadata={"args_count": len(args), "kwargs_keys": list(kwargs.keys())},
            )
            if accepts_span_id:
                kwargs.setdefault("span_id", span.span_id)
            try:
                result = fn(*args, **kwargs)
                span.finish()
                return result
            except Exception as exc:
                span.finish(error=str(exc))
                raise

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            span = tracer.start_span(
                name=span_name,
                parent_id=parent_id,
                metadata={"args_count": len(args), "kwargs_keys": list(kwargs.keys())},
            )
            if accepts_span_id:
                kwargs.setdefault("span_id", span.span_id)
            try:
                result = await fn(*args, **kwargs)
                span.finish()
                return result
            except Exception as exc:
                span.finish(error=str(exc))
                raise

        if inspect.iscoroutinefunction(fn):
            return async_wrapper
        return wrapper

    return decorator
