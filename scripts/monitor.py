#!/usr/bin/env python3
"""monitor.py: Continuous live monitoring with auto-correction"""
import os, time, json, subprocess as sp

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_git():
    r = sp.run("git status --short", shell=True, capture_output=True, text=True, cwd=B, timeout=5)
    return {"dirty": len(r.stdout.strip()) > 0, "files": r.stdout.strip().split("\n")[:5]}

def check_ports():
    ports = {}
    for p in [8888, 9223, 6080]:
        r = sp.run(f"curl -s --max-time 2 http://127.0.0.1:{p}", shell=True, capture_output=True, text=True, timeout=5)
        ports[p] = "UP" if r.returncode == 0 else "DOWN"
    return ports

def auto_fix():
    fixes = []
    git = check_git()
    if git["dirty"]:
        sp.run("git add -A && git commit -m 'auto-fix: live monitor checkpoint'", shell=True, cwd=B, timeout=10)
        fixes.append("git_committed")
    return fixes

def loop():
    while True:
        state = {
            "timestamp": time.time(),
            "git": check_git(),
            "ports": check_ports(),
            "fixes": auto_fix()
        }
        with open(f"{B}/env/monitor.json", "a") as f:
            f.write(json.dumps(state) + "\n")
        time.sleep(60)

if __name__ == "__main__":
    loop()
