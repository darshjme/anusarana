# agent-tracer

**Execution tracing and call graph for AI agents.**

Agents call tools, sub-agents, and APIs in complex chains. When something fails, `agent-tracer` gives you the full trace:

```
agent.run → tool.search → api.fetch → ❌ ConnectionError
```

Zero dependencies. Pure Python 3.10+.

---

## Installation

```bash
pip install agent-tracer
```

---

## Quick Start

### Basic Tracing

```python
from agent_tracer import Tracer

tracer = Tracer()

# Agent root span
agent_span = tracer.start_span("agent.run")

# Tool call child span
tool_span = tracer.start_span("tool.search", parent_id=agent_span.span_id, metadata={"query": "LLM papers"})

# API call grandchild span
api_span = tracer.start_span("api.fetch", parent_id=tool_span.span_id, metadata={"url": "https://api.example.com"})

# Simulate API failure
tracer.finish_span(api_span.span_id, error="ConnectionError: timed out")
tracer.finish_span(tool_span.span_id, error="API call failed")
tracer.finish_span(agent_span.span_id, error="tool failed")

# Inspect the trace
import json
print(json.dumps(tracer.to_dict(), indent=2))
```

Output:
```json
{
  "trace_id": "...",
  "spans": [
    {
      "name": "agent.run",
      "status": "error",
      "error": "tool failed",
      "children": [
        {
          "name": "tool.search",
          "status": "error",
          "children": [
            {
              "name": "api.fetch",
              "status": "error",
              "error": "ConnectionError: timed out",
              "children": []
            }
          ]
        }
      ]
    }
  ],
  "total_spans": 3
}
```

---

### @trace_call Decorator

```python
from agent_tracer import Tracer, trace_call

tracer = Tracer()

@trace_call(tracer, name="agent.run")
def run_agent(task: str):
    result = call_tool(task)
    return result

@trace_call(tracer, name="tool.web_search")
def call_tool(query: str, span_id: str = None):
    # span_id is injected automatically when accepted
    print(f"Searching with span: {span_id}")
    return fetch_api(query, parent_span=span_id)

def fetch_api(query, parent_span=None):
    api_span = tracer.start_span("api.fetch", parent_id=parent_span, metadata={"query": query})
    try:
        # ... do real API call ...
        tracer.finish_span(api_span.span_id)
        return {"results": []}
    except Exception as e:
        tracer.finish_span(api_span.span_id, error=str(e))
        raise

run_agent("find recent LLM papers")

# Print call graph
for span in tracer.spans:
    indent = "  " if span.parent_id else ""
    print(f"{indent}[{span.status}] {span.name} ({span.duration_ms:.1f}ms)")
```

---

### Async Support

```python
import asyncio
from agent_tracer import Tracer, trace_call

tracer = Tracer()

@trace_call(tracer, name="async.agent")
async def async_agent():
    await asyncio.sleep(0.1)
    return "done"

asyncio.run(async_agent())
print(tracer.spans[0].status)  # success
```

---

## API Reference

### `Span`

| Attribute/Method | Type | Description |
|-----------------|------|-------------|
| `span_id` | `str` | UUID4 identifier |
| `name` | `str` | Operation name |
| `parent_id` | `str \| None` | Parent span ID |
| `metadata` | `dict` | Arbitrary key-value context |
| `start_time` | `float` | Unix timestamp |
| `end_time` | `float \| None` | Unix timestamp when finished |
| `status` | `str` | `"active"`, `"success"`, or `"error"` |
| `error` | `str \| None` | Error message if failed |
| `duration_ms` | `float \| None` | Duration in milliseconds |
| `finish(error=None)` | method | Mark span complete |
| `to_dict()` | `dict` | Serialize to dictionary |

### `Tracer`

| Method | Description |
|--------|-------------|
| `start_span(name, parent_id, metadata)` | Create and register a span |
| `finish_span(span_id, error)` | Finish a span by ID |
| `get_span(span_id)` | Retrieve span by ID |
| `spans` | All spans (list) |
| `root_spans` | Spans without parents |
| `children_of(span_id)` | Direct children of a span |
| `to_dict()` | Full nested trace dict |

### `@trace_call(tracer, name, parent_id)`

Wraps sync or async functions. If the function signature includes `span_id`, the active span's ID is injected automatically.

---

## License

MIT
