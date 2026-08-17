#!/usr/bin/env python3
import os, subprocess as sp, sys

PAT = os.environ.get("GITHUB_PAT", "")
REPO = "toxicwind/ontological-atlas"

def push(branch="main"):
    if not PAT:
        return {"err": "GITHUB_PAT not set"}
    sp.run("git config --global --add safe.directory '*'", shell=True)
    sp.run(f"git remote set-url origin https://toxicwind:{PAT}@github.com/{REPO}.git", shell=True)
    r = sp.run(f"git push -f origin {branch}", shell=True, capture_output=True, text=True, timeout=30)
    return {"rc": r.returncode, "out": r.stdout, "err": r.stderr}

if __name__ == "__main__":
    import json
    print(json.dumps(push(sys.argv[1] if len(sys.argv) > 1 else "main"), indent=1))
