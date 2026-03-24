# Contributing

Thank you for considering contributing to **agent-tracer**!

## Getting Started

```bash
git clone https://github.com/darshjme-codes/agent-tracer
cd agent-tracer
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Guidelines

- Keep zero runtime dependencies — `agent-tracer` must remain a pure stdlib library.
- All new features must include tests. Aim for ≥30 tests total.
- Use type hints throughout.
- Follow existing code style (PEP 8, f-strings, `from __future__ import annotations`).
- Open an issue before large refactors.

## Pull Request Process

1. Fork the repo and create a feature branch.
2. Write tests for your change.
3. Ensure all tests pass: `python -m pytest tests/ -v`.
4. Submit a PR with a clear description of the change.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
