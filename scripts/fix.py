#!/usr/bin/env python3
import os, subprocess as sp

def fix_all():
    sp.run("git config --global --add safe.directory '*'", shell=True)
    sp.run("git config --global user.name toxicwind", shell=True)
    sp.run("git config --global user.email toxicwind@users.noreply.github.com", shell=True)
    sp.run("chmod -R 777 /mnt/agents/output 2>/dev/null", shell=True)
    return {"status": "fixed"}

if __name__ == "__main__":
    import json
    print(json.dumps(fix_all(), indent=1))
