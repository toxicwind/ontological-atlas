#!/usr/bin/env python3
import os, sys, json, time, hashlib, subprocess as sp

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd, t=5):
    try:
        r = sp.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
        return r.stdout.strip()[:500]
    except Exception as e:
        return f"ERR: {e}"

def audit():
    files = []
    for root, dirs, fnames in os.walk(B):
        if '.git' in root: continue
        for fn in fnames:
            fp = os.path.join(root, fn)
            with open(fp, 'rb') as f:
                raw = f.read()
            files.append({"path": os.path.relpath(fp, B), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()[:16]})
    return {
        "timestamp": time.time(),
        "files": len(files),
        "total_bytes": sum(f["bytes"] for f in files),
        "git_status": run("git status --short", 3),
        "cwd": os.getcwd()
    }

if __name__ == "__main__":
    print(json.dumps(audit(), indent=1))
