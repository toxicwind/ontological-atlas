# Operating Contract

## Environment

- /tmp wipes between turns
- /mnt/agents/output persists
- Python 3.12, no sudo
- 108s total timeout per turn
- 25 tool calls per turn

## Design Principles

1. Subprocess over REPL
2. Parallel over sequential
3. Persistent over temporary
4. Fallback over failure

## CVE-2026-TOOLGATE

Tool invocation gateway returns 504 under sustained load. Workaround: use local Python file operations, bypass gateway.
