#!/usr/bin/env python3
"""OSINT async parallel scraper."""
import asyncio, sys, re, json, urllib.parse as up
from pathlib import Path

async def fetch(q, sem):
    async with sem:
        u = f"https://www.bing.com/search?q={up.quote(q)}"
        p = await asyncio.create_subprocess_shell(
            f"curl -s -L --connect-timeout 2 --max-time 8 -A 'Mozilla/5.0' '{u}'",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        o, _ = await p.communicate()
        h = o.decode('utf-8', errors='ignore')
        links = re.findall(r'href="(https?://[^"]+)"', h)
        return {"query": q, "links": links[:10]}

async def main(queries):
    sem = asyncio.Semaphore(4)
    tasks = [fetch(q, sem) for q in queries]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(json.dumps(r))

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
