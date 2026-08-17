#!/usr/bin/env python3
"""swarm.py: Background task orchestrator for pi, zed, mcpproxy, llama-swap"""
import os, subprocess as sp, time, json, signal

TASKS = {
    "pi": {"cmd": "python3 -m pi.zed", "log": "/mnt/agents/output/av/swarm_pi.log"},
    "mcpproxy": {"cmd": "python3 -m mcpproxy", "log": "/mnt/agents/output/av/swarm_mcp.log"},
    "llama_swap": {"cmd": "python3 -m llama_swap", "log": "/mnt/agents/output/av/swarm_llama.log"},
}

def start_all():
    for name, cfg in TASKS.items():
        os.makedirs(os.path.dirname(cfg["log"]), exist_ok=True)
        with open(cfg["log"], "a") as log:
            log.write(f"[{time.time()}] Starting {name}\n")
        sp.Popen(
            cfg["cmd"], shell=True,
            stdout=open(cfg["log"], "a"),
            stderr=open(cfg["log"], "a"),
            preexec_fn=os.setsid
        )
    return {"started": list(TASKS.keys())}

def status():
    return {name: os.path.exists(f"/proc/{sp.run(f'pgrep -f {name}', shell=True, capture_output=True, text=True).stdout.strip()}") for name in TASKS}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print(json.dumps(status(), indent=1))
    else:
        print(json.dumps(start_all(), indent=1))
