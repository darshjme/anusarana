# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-25

### Added
- `Span` class with full lifecycle management (`active` → `success`/`error`)
- `Tracer` class for managing trace trees with nested span support
- `@trace_call` decorator for automatic span creation around function calls
- Async function support in `@trace_call`
- `span_id` injection into decorated functions that accept it
- `children_of()` and `root_spans` for traversing the call graph
- `to_dict()` serialization on both `Span` and `Tracer` (nested)
- Zero external dependencies — pure Python 3.10+
