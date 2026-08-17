#!/usr/bin/env python3
import os, json, time, hashlib

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_structure():
    required = ["SKILL.md", "AGENTS.md", "README.md"] + [f"modules/0{i}-*" for i in range(1,8)]
    return {item: os.path.exists(os.path.join(B, item)) for item in required}

def test_scripts():
    return {s: os.path.exists(os.path.join(B, "scripts", s)) for s in ["loader.py","audit.py","fix.py","push.py","test.py"]}

def run():
    return {"timestamp": time.time(), "structure": test_structure(), "scripts": test_scripts()}

if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
