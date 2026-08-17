#!/usr/bin/env python3
import os, sys, subprocess as sp, json, time

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def boot():
    os.makedirs(f"{B}/env/venv", exist_ok=True)
    os.makedirs(f"{B}/env/apt", exist_ok=True)
    os.makedirs(f"{B}/env/bin", exist_ok=True)
    sp.run("git config --global --add safe.directory '*'", shell=True)
    sp.run("git config --global user.name toxicwind", shell=True)
    sp.run("git config --global user.email toxicwind@users.noreply.github.com", shell=True)
    return {"status": "booted", "time": time.time()}

if __name__ == "__main__":
    print(json.dumps(boot(), indent=1))
