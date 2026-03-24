# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

If you discover a security vulnerability in **agent-tracer**, please **do not** open a public GitHub issue.

Instead, email **darshjme@gmail.com** with:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge your report within 48 hours and aim to release a fix within 7 days for critical issues.

## Scope

agent-tracer is a pure-Python tracing library with zero external dependencies. Its attack surface is limited to:
- Metadata stored in spans (user-controlled; do not store secrets)
- `to_dict()` serialization (safe for logging/export — avoid sending to untrusted endpoints)
