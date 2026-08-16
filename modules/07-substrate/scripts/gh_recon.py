#!/usr/bin/env python3
import os, sys, json, subprocess as sp2, time

PAT = os.environ.get("GITHUB_PAT", "")
USER = "toxicwind"

def api(path):
    h = f"Authorization: token {PAT}"
    a = "Accept: application/vnd.github.v3+json"
    c = f'curl -s -H "{h}" -H "{a}" --max-time 8 "https://api.github.com{path}"'
    r = sp2.run(c, shell=True, capture_output=True, text=True, timeout=10)
    try:
        return json.loads(r.stdout)
    except:
        return {"err": r.stdout[:200] + "|" + r.stderr[:200]}

def repos(per_page=100):
    out = []
    page = 1
    while True:
        d = api(f"/users/{USER}/repos?per_page={per_page}&page={page}&sort=pushed&direction=desc")
        if isinstance(d, list):
            out.extend(d)
            if len(d) < per_page:
                break
            page += 1
        else:
            print(json.dumps({"err": d}, indent=1))
            break
    return out

def recent(repos_list, days=7):
    now = time.time()
    cutoff = now - (days * 24 * 3600)
    rec = []
    for r in repos_list:
        pushed = r.get("pushed_at", "")
        if pushed:
            try:
                ts = time.mktime(time.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ"))
                if ts >= cutoff:
                    rec.append({
                        "name": r["name"],
                        "private": r.get("private", False),
                        "pushed_at": pushed,
                        "html_url": r["html_url"],
                        "description": r.get("description", "")
                    })
            except:
                pass
    return rec

if __name__ == "__main__":
    if not PAT:
        print("GITHUB_PAT not set")
        sys.exit(1)
    print(f"Fetching repos for {USER}...")
    all_repos = repos()
    print(f"Total repos: {len(all_repos)}")
    rec = recent(all_repos, days=7)
    print(f"Recent (7d): {len(rec)}")
    for r in rec:
        vis = "PRIVATE" if r["private"] else "PUBLIC"
        print(f"  [{vis}] {r['name']} — {r['pushed_at']}")
    out = "/mnt/agents/output/ontological-atlas/modules/07-substrate/scripts/gh_recon.json"
    with open(out, "w") as f:
        json.dump({"user": USER, "total": len(all_repos), "recent_7d": rec, "timestamp": time.time()}, f, indent=1)
    print(f"Saved to {out}")
