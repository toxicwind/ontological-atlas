#!/usr/bin/env python3
import os, sys, json

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test():
    required = ["SKILL.md", "AGENTS.md", "README.md", "scripts/loader.py", "scripts/audit.py"]
    results = {}
    for item in required:
        results[item] = os.path.exists(os.path.join(B, item))
    return {"all_pass": all(results.values()), "items": results}

if __name__ == "__main__":
    print(json.dumps(test(), indent=1))
