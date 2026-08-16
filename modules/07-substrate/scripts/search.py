#!/usr/bin/env python3
import sys, os, re, json, time, asyncio

T0 = time.time()
def log(*a):
    print(f"[+{time.time()-T0:8.3f}s]", *a, flush=True)

HOSTS = ["http://mirrors.cloud.aliyuncs.com", "https://mirrors.aliyun.com"]
REPOS = ["pypi","pytorch-wheels","apt","ubuntu","ubuntu-ports","debian","debian-security","centos",
"centos-vault","epel","fedora","alinux","almalinux","rocky","openEuler","anolis","docker-ce",
"kubernetes","kali","archlinux","alpine","termux","npm","nodejs","nodejs-release","golang","rustup",
"maven","gradle","composer","homebrew","homebrew-bottles","anaconda","miniconda","cygwin","gnu",
"CTAN","CRAN","bioconductor","jenkins","elasticstack","grafana","mongodb","mysql","postgresql",
"libreoffice","blender","gimp","videolan","zabbix","saltstack","chef","puppet","qemu","gitlab-ce"]

async def cu(u, mx=6):
    try:
        p = await asyncio.create_subprocess_shell(
            f'curl -s --connect-timeout 2 --max-time {mx} "{u}"',
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        o, _ = await asyncio.wait_for(p.communicate(), mx + 2)
        return o.decode("utf-8", "replace")
    except Exception:
        return ""

async def ps(u):
    try:
        p = await asyncio.create_subprocess_shell(
            f'curl -s --connect-timeout 2 --max-time 5 -o /dev/null -w "%{{http_code}}" "{u}"',
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        o, _ = await asyncio.wait_for(p.communicate(), 7)
        return o.decode().strip()
    except Exception:
        return "000"

async def rep():
    pairs = [(h, r) for h in HOSTS for r in REPOS]
    rs = await asyncio.gather(*[ps(f"{h}/{r}/") for h, r in pairs])
    live = {}
    for (h, r), c in zip(pairs, rs):
        if c.startswith("2") or c == "301":
            live.setdefault(r, h)
    log(f"LIVE_REPOS={len(live)}")
    for r in sorted(live):
        print(f"{r:20s} {live[r]}/{r}/")
    open("/mnt/agents/output/av/repos.json", "w").write(json.dumps(live, indent=1, sort_keys=True))
    return live

async def sea(q):
    hits = []
    async def pypi(name):
        c = await ps(f"https://mirrors.aliyun.com/pypi/simple/{name}/")
        if c.startswith("2"):
            hits.append(("pypi", name, f"https://mirrors.aliyun.com/pypi/simple/{name}/"))
    tasks = [pypi(q), pypi(q.lower()), pypi(q.replace("_", "-"))]
    for r in REPOS:
        tasks.append(ps(f"https://mirrors.aliyun.com/{r}/"))
    await asyncio.gather(*tasks)
    try:
        live = json.load(open("/mnt/agents/output/av/repos.json"))
    except Exception:
        live = {}
    for r, h in live.items():
        if q.lower() in r.lower():
            hits.append(("repo", r, f"{h}/{r}/"))
    for k, n, u in hits:
        print(f"{k:6s} {n:30s} {u}")
    if not hits:
        log("NO_HITS", q)
    return hits

async def lst(repo, pat=""):
    u = f"https://mirrors.aliyun.com/{repo}/"
    h = await cu(u)
    a = sorted(set(re.findall(r'href="([^"?/][^"]*)/"', h)))
    for x in a:
        if not pat or re.search(pat, x, re.I):
            print(x)

def main():
    a = sys.argv[1:]
    if not a:
        print("search.py repos | search.py find <q> | search.py ls <repo> [regex]")
        return
    try:
        if a[0] == "repos":
            asyncio.run(rep())
        elif a[0] == "find" and len(a) > 1:
            asyncio.run(sea(a[1]))
        elif a[0] == "ls" and len(a) > 1:
            asyncio.run(lst(a[1], a[2] if len(a) > 2 else ""))
        else:
            print("search.py repos | find <q> | ls <repo> [regex]")
    except Exception as e:
        log("SEARCH_EXC", str(e)[:100])

if __name__ == "__main__":
    main()
