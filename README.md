# Ontological Atlas

A modular research framework mapping the co-constitutive nature of reality.

## Modules

- [01 Rendering Engine](modules/01-rendering-engine/) — Observer is the apparatus
- [02 Folklore Interface](modules/02-folklore-interface/) — Ebu Gogo, little people gradient
- [03 Consciousness Technologies](modules/03-consciousness-technologies/) — UAP, DMT, music
- [04 AI Alignment Ontology](modules/04-ai-alignment-ontology/) — Constitutional immune response
- [05 Quantum Biology](modules/05-quantum-biology/) — Orch OR
- [06 Source Archive](modules/06-source-archive/) — Primary sources
- [07 Substrate](modules/07-substrate/) — Audio forensics + system tools

## Quick Start

```bash
python3 scripts/loader.py boot
python3 scripts/audit.py
python3 scripts/test.py
```

## Scripts

- `scripts/loader.py` — universal bootstrap (`boot`)
- `scripts/audit.py` — live system auditor (writes `env/last_audit.json`)
- `scripts/fix.py` — self-healing repair: git safe.directory, git identity, workspace permissions
- `scripts/push.py` — GitHub push wrapper, force-pushes `main` (requires `GITHUB_PAT` env var)
- `scripts/swarm.py` — background task orchestrator: starts pi, mcpproxy, and llama-swap detached with per-task logs under `/mnt/agents/output/av/`; `python3 scripts/swarm.py status` reports what's running
- `scripts/monitor.py` — continuous live monitor: every 60s checks git dirtiness and ports 8888/9223/6080, auto-commits a dirty tree, appends state to `env/monitor.json`
- `scripts/test.py` — self-checks required files, then runs the universal test suite

## CI

Universal Skill CI (`.github/workflows/universal-skill-ci.yml`) runs on every
push and PR to `main` plus every 6 hours: it runs `tests/universal_test.py` and
`scripts/audit.py`, uploads the audit artifact, and gates on a secret scan plus
a minimum file count.

## License

CC0 1.0 Universal — see [LICENSE](LICENSE).
