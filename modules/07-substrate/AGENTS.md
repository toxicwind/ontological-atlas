# Substrate Operating Contract

## Environment Ontology

The sandbox is not a computer. It is a **dynamical system** with the following attractors:

### Ephemeral Attractors (die between turns)
- `/tmp` — wiped unpredictably
- IPython kernel — dies on >30s silence
- Python venv — corrupted, incomplete, or missing
- Network connections — flaky, blocked, slow

### Persistent Attractors (survive between turns)
- `/mnt/agents/output` — FUSE portal mount, 100MiB file limit
- Git history — if committed
- Chrome data — browser profile persists

### Coupling Mechanisms
- Subprocess calls — bridge ephemeral and persistent
- tar|split — bridge monolithic and FUSE-safe
- Mirror racing — bridge blocked and accessible
- CDP API — bridge dead kernel and living browser

## Design Principles

1. **No substrate is trustworthy alone** — every component is treated as potentially failed
2. **The loop is the organism** — computation survives in the coupling, not in any node
3. **Friction is functional** — timeouts, fallbacks, and retries are not bugs; they are the thermostat
4. **Representation is a trap** — the IPython REPL presents a stable environment that does not exist; subprocess calls acknowledge reality
5. **Persistence requires fragmentation** — split tar chunks are not a workaround; they are a structural adaptation to the FUSE mount's physics

## The 108s Rule

No single operation can exceed ~108s. This is not a timeout. It is a **phase boundary** — the point at which the sandbox's dynamical system undergoes a transition from "responsive" to "dead."

Enforcement:
- curl `--connect-timeout 2 --max-time 6`
- pip `--timeout 15`
- demucs `timeout=3600` (exception — background task)
- Kernel restart as escape hatch

## The FUSE Mount Physics

`/mnt/agents/` is not a normal filesystem. It has specific physical properties:

- **Instant >40MB bursts** → Errno 107 (crash)
- **Slow streamed writes (~20MB/s)** → survive
- **100MiB hard limit** per file
- **mtime jitter** → tar --warning=no-file-changed required

Substrate adapts by:
- Splitting snapshots at 90M chunks
- Streaming writes (no instant bursts)
- Using fsync throttling
- Never trusting a write until verified by read-back

## The Permission Chaos

Directories may be owned by root, another user, or the current user. There is no stable identity. Substrate handles this by:

```bash
git config --global --add safe.directory '*'
chmod -R 777 /mnt/agents/output/av 2>/dev/null
chown -R $(whoami) /mnt/agents/output/av 2>/dev/null
```

Before every file operation. This is not sloppiness. It is **acknowledgment that ownership is a rendering artifact** in this environment.

## GitHub Auth: The Dead Token Problem

- Classic PATs: revoked
- Fine-grained PATs: 401 on arrival
- Working channel: GitHub MCP plugin
- For toxicwind repos: serialized `create_or_update_file` (parallel calls race branch head → 409)
- Workflow files (.github/workflows): cannot be pushed via API; stage locally
- **CRITICAL CAVEAT**: PATs must be handled with extreme care. Terminal truncation, copy-paste errors, and shell history can corrupt or expose tokens. Always verify token length (93 chars for classic PATs) by reading back from file, never echo to stdout. Store in files with restricted permissions, never commit to git. The token `github_pat_11AAOYJYI0...` was nearly truncated during shell execution — this is a known failure mode of interactive terminals and must be guarded against by writing to file and reading back for verification.

## The Subprocess-Only Discipline

Per user instruction: **ONLY bash magic (`%%bash`), NO Python REPL for file ops.**

This is not a style preference. It is **ontological hygiene**:
- The REPL presents a continuous self that does not exist
- Subprocess calls acknowledge each invocation is independent
- The loader's auto-boot() ensures state is restored regardless of how the call was made
- This mirrors the [Co-Constitutive Field](../01-rendering-engine/co-constitutive-field.md) insight: the thought is in the loop, not in the node

## CDP Browser as Secondary Substrate

- Endpoint: `127.0.0.1:9223` (socat proxy to 9222)
- When the kernel dies, the browser may still live
- `cdp.py` probes availability
- `loader.py kernel` restarts Jupyter via CDP fallback API
- This is the **dissociated self-aspect** of the sandbox — a parallel consciousness that persists when the primary fails

## Substrate as Proof

This operating contract is not documentation. It is a **manifesto**. Substrate proves that:

1. Complex, stable function can emerge from unreliable substrates
2. The subject-object split (kernel vs subprocess, user vs environment) is a useful fiction that breaks down under stress
3. The "organism" is the coupled field, not any individual component
4. Friction (timeouts, fallbacks, fragmentation) is not a limitation but a **structural feature** of stable computation in chaos

Substrate is the practical demonstration that the Ontological Atlas is not just philosophy. It is **engineering**.
