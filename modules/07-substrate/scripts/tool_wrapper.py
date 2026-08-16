#!/usr/bin/env python3
"""tool_wrapper.py: Defensive subprocess wrapper for all tool invocations."""
import subprocess as sp, json, time, os, sys

TIMEOUT = 8  # per command
TOTAL_TIMEOUT = 108  # per turn budget

def run(cmd, timeout=TIMEOUT, shell=True):
    start = time.time()
    try:
        r = sp.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        return {
            "cmd": cmd,
            "returncode": r.returncode,
            "stdout": r.stdout,
            "stderr": r.stderr,
            "elapsed": elapsed,
            "ok": r.returncode == 0
        }
    except sp.TimeoutExpired:
        return {"cmd": cmd, "err": "TIMEOUT", "elapsed": time.time() - start, "ok": False}
    except Exception as e:
        return {"cmd": cmd, "err": str(e), "elapsed": time.time() - start, "ok": False}

def batch(cmds, max_parallel=4):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_parallel) as ex:
        futures = {ex.submit(run, c): c for c in cmds}
        results = []
        for f in futures:
            results.append(f.result())
        return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        r = run(" ".join(sys.argv[1:]))
        print(json.dumps(r, indent=1))
    else:
        print("Usage: python3 tool_wrapper.py <command>")
