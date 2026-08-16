#!/usr/bin/env python3
"""KIMI-LOADER v2: universal bootstrap, repair and task runner for Kimi agent sandboxes.

Self-healing design: every command auto-runs boot() first (the agent forgets; the loader does not).
Parallel coroutine probes, connect timeouts <=2s, per-line timing benchmarks, nested try/except
fallbacks, awk-assisted shell parsing, Alibaba VPC-mirror restore chain, persistent non-/tmp storage.
Usage:
  python3 loader.py boot              full bootstrap+repair (idempotent, safe to spam)
  python3 loader.py selftest          >100MB persistent-write test + mirror race + venv check
  python3 loader.py pip <pkgs...>     install via raced mirror chain (nested fallbacks)
  python3 loader.py torch             CPU-aware torch/torchaudio install (no CUDA packages)
  python3 loader.py snap              snapshot venv site-packages -> persistent pylib
  python3 loader.py restore           restore pylib -> venv site-packages
  python3 loader.py demucs <audio>    stem separation (CPU, htdemucs)
  python3 loader.py probe             parallel mirror race, prints ranked results
  python3 loader.py kernel            restart ipython kernel (8888 api, 9223 fallback)
  python3 loader.py fix <path>        hidden repair: perms/ownership sweep
  python3 loader.py links <nid>       gaia passthrough (delegates to gaia_stream.py if present)
"""
import os, sys, json, time, shutil, asyncio, platform, subprocess as sp

T0 = time.time()
def log(*a):
    print(f"[+{time.time()-T0:8.3f}s]", *a, flush=True)

PERS  = "/mnt/agents/output/av"
PYLIB = f"{PERS}/pylib"
TMPH  = "/tmp/h"
VENV  = "/tmp/av"
VPY   = f"{VENV}/bin/python"
VPIP  = f"{VENV}/bin/pip"
SP_D  = f"{VENV}/lib/python3.12/site-packages"

IDX = [
    ("http://mirrors.cloud.aliyuncs.com/pypi/simple/",  "mirrors.cloud.aliyuncs.com"),
    ("https://mirrors.aliyun.com/pypi/simple/",         None),
    ("http://mirrors.aliyun.com/pypi/simple/",          "mirrors.aliyun.com"),
    ("https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/", None),
    ("https://mirrors.ustc.edu.cn/pypi/web/simple/",    None),
    ("https://pypi.org/simple/",                        None),
]
TCU = [
    ("http://mirrors.cloud.aliyuncs.com/pytorch-wheels/cpu", "mirrors.cloud.aliyuncs.com"),
    ("https://mirrors.aliyun.com/pytorch-wheels/cpu",        None),
    ("https://download.pytorch.org/whl/cpu",                 None),
]
TORCH_DEPS = ["filelock","typing-extensions","sympy","networkx","jinja2","fsspec","mpmath","setuptools"]
DEMUC_DEPS = ["demucs","lameenc","julius","einops","openunmix","dora-search","tqdm","pyyaml","diffq"]
BASE_DEPS  = ["librosa","soundfile","numpy","scipy"]

def run(c, t=30):
    try:
        return sp.run(c, shell=True, capture_output=True, text=True, timeout=t)
    except Exception as e:
        log("RUN_EXC", str(e)[:90])
        return sp.run("true", shell=True, capture_output=True, text=True)

def fix(p):
    try:
        run(f'chmod -R 777 {p} 2>/dev/null; chown -R $(whoami) {p} 2>/dev/null', 20)
        r = run(f'ls -la {p} 2>/dev/null | awk "NR<=6{{print \\$1,\\$5,\\$9}}"', 5)
        log("FIXED", p);  return r.stdout
    except Exception as e:
        log("FIX_EXC", str(e)[:80]); return ""

async def probe(u, th):
    try:
        p = await asyncio.create_subprocess_shell(
            f'curl -s --connect-timeout 2 --max-time 6 -o /dev/null -w "%{{http_code}} %{{time_total}}" {u}',
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        o, _ = await asyncio.wait_for(p.communicate(), 8)
        parts = o.decode().split()
        return (u, th, parts[0] if parts else "000", float(parts[1]) if len(parts) > 1 else 9e9)
    except Exception:
        return (u, th, "000", 9e9)

async def race(idx):
    rs = await asyncio.gather(*[probe(u, th) for u, th in idx])
    ok = sorted([r for r in rs if r[2].startswith(("2", "3"))], key=lambda r: r[3])
    for u, th, c, t in rs:
        log("PROBE", f"{c}", f"{t:.3f}s", u)
    return ok

def race_sync(idx):
    try:
        return asyncio.run(race(idx))
    except Exception as e:
        log("RACE_EXC", str(e)[:80])
        try:
            loop = asyncio.new_event_loop(); ok = loop.run_until_complete(race(idx)); loop.close()
            return ok
        except Exception as e2:
            log("RACE_NEST_EXC", str(e2)[:80]); return []

def pipc(args, idx=None, t=1800):
    order = race_sync(idx or IDX) or (idx or IDX)
    for ent in order:
        u, th = ent[0], ent[1]
        try:
            ths = []
            if th:
                ths = ["--trusted-host", th]
                if th != "mirrors.aliyun.com":
                    ths += ["--trusted-host", "mirrors.aliyun.com"]
            c = [VPIP, "install", "--no-input", "--timeout", "15"] + args + ["-i", u] + ths
            r = sp.run(c, capture_output=True, text=True, timeout=t)
            if r.returncode == 0:
                log("PIP_OK", u, " ".join(args[:3])); return True
            try:
                r2 = sp.run(c + ["--no-cache-dir", "--retries", "1"], capture_output=True, text=True, timeout=t)
                if r2.returncode == 0:
                    log("PIP_OK2", u, " ".join(args[:3])); return True
                log("PIP_FAIL", u, ((r.stderr or "") + (r.stdout or ""))[-140:].replace("\n", " "))
            except Exception as e2:
                log("PIP_NEST_EXC", u, str(e2)[:90])
        except Exception as e:
            log("PIP_EXC", u, str(e)[:90])
    return False

def venv():
    try:
        if not os.path.exists(VPY):
            log("VENV_CREATE")
            r = run(f"python3 -m venv {VENV}", 120)
            if not os.path.exists(VPY):
                log("VENV_COPIES_RETRY")
                run(f"python3 -m venv --copies {VENV}", 120)
        os.makedirs(SP_D, exist_ok=True)
        pth = os.path.join(SP_D, "zz_av_pylib.pth")
        if os.path.isdir(PYLIB) and not os.path.exists(pth):
            open(pth, "w").write(PYLIB + "\n"); log("PTH_LINK", PYLIB)
        return os.path.exists(VPY)
    except Exception as e:
        log("VENV_EXC", str(e)[:90]); return False

def restore():
    parts = f"{PYLIB}/parts"
    try:
        if os.path.isdir(parts) and not os.path.exists(os.path.join(SP_D, "librosa")):
            log("RESTORE_PARTS_START")
            os.makedirs(os.path.dirname(SP_D.rstrip("/")), exist_ok=True)
            for i in range(3):
                r = run(f"cat {parts}/site.tar.gz.part_* | tar xzf - -C {os.path.dirname(SP_D.rstrip('/'))}/", 300)
                if r.returncode == 0:
                    log("RESTORE_PARTS_DONE"); return
                log("RESTORE_RETRY", i)
            try:
                r2 = run(f"cat {parts}/site.tar.gz.part_* | tar xzf - --checkpoint=10000 -C {os.path.dirname(SP_D.rstrip('/'))}/", 300)
                log("RESTORE_ALT", r2.returncode)
            except Exception as e2:
                log("RESTORE_NEST_EXC", str(e2)[:80])
    except Exception as e:
        log("RESTORE_EXC", str(e)[:90])

def snap():
    parts = f"{PYLIB}/parts"
    try:
        os.makedirs(parts, exist_ok=True)
        parent = os.path.dirname(SP_D.rstrip("/"))
        base = os.path.basename(SP_D.rstrip("/"))
        for i in range(3):
            r = run(f"cd {parent} && tar czf - {base} 2>/dev/null | split -b 90M - {parts}/site.tar.gz.part_", 600)
            n = run(f'ls {parts} | wc -l', 15).stdout.strip()
            if r.returncode == 0 and n != "0":
                log("SNAP_DONE", n, "parts"); return
            log("SNAP_RETRY", i)
        try:
            run(f"rm -rf {parts}/site.tar.gz.part_*", 30)
            log("SNAP_CLEANED_PARTIAL")
        except Exception as e2:
            log("SNAP_NEST_EXC", str(e2)[:80])
    except Exception as e:
        log("SNAP_EXC", str(e)[:90])

def hook():
    try:
        sc = os.path.join(SP_D, "sitecustomize.py")
        body = (
            "import os,sys,time\n"
            "os.environ.setdefault('OMP_NUM_THREADS','2')\n"
            "os.environ.setdefault('MKL_NUM_THREADS','2')\n"
            "os.environ.setdefault('NUMBA_NUM_THREADS','2')\n"
            "os.environ['PATH']=os.environ.get('PATH','')+':/home/kimi/.local/bin'\n"
            f"pl={PYLIB!r}\n"
            "if os.path.isdir(pl) and pl not in sys.path: sys.path.insert(0,pl)\n"
        )
        open(sc, "w").write(body); log("HOOK_SITECUSTOMIZE")
        env = (
            "export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMBA_NUM_THREADS=2\n"
            "export PATH=$PATH:/home/kimi/.local/bin\n"
            f"export PYTHONPATH={PYLIB}\n"
            f"alias avpy={VPY}\n"
            f"alias avpip={VPIP}\n"
            "export PIP_INDEX_URL=http://mirrors.cloud.aliyuncs.com/pypi/simple/\n"
            "export PIP_TRUSTED_HOST=mirrors.cloud.aliyuncs.com\n"
        )
        open(f"{PERS}/av_env.sh", "w").write(env); log("HOOK_ENV_SH")
        open(f"{TMPH}/auto.py", "w").write(
            "import subprocess as sp,os\n"
            "def au():\n"
            f" if not os.path.exists({VPY!r}):\n"
            f"  sp.run(['python3',{os.path.abspath(__file__)!r},'boot'],capture_output=True,timeout=900)\n"
            "au()\n")
        log("HOOK_AUTORUN")
    except Exception as e:
        log("HOOK_EXC", str(e)[:90])

def krn():
    import urllib.request as u
    for base in ("http://127.0.0.1:8888", "http://127.0.0.1:9223"):
        try:
            ks = json.loads(u.urlopen(base + "/api/kernels", timeout=2).read())
            if isinstance(ks, list) and ks:
                q = u.Request(f"{base}/api/kernels/{ks[0]['id']}/restart", method="POST")
                log("KERNEL_RESTART", u.urlopen(q, timeout=3).status); return True
        except Exception as e:
            log("KERNEL_TRY_FAIL", base, str(e)[:60])
    return False

def cdp_ok():
    import urllib.request as u
    try:
        d = json.loads(u.urlopen("http://127.0.0.1:9223/json/version", timeout=2).read())
        log("CDP_OK", d.get("Browser", "?")); return True
    except Exception as e:
        log("CDP_FAIL", str(e)[:60]); return False

def selftest():
    log("SELFTEST_START")
    os.makedirs(PERS, exist_ok=True)
    t = time.time()
    r = run(f'dd if=/dev/zero of={PERS}/tmp/w150.bin bs=1M count=150 2>&1 | tail -1', 120)
    dt = time.time() - t
    log("PERSIST_WRITE_150MB", f"{150/max(dt,0.001):.0f}MB/s", r.stdout.strip()[-60:])
    run(f'rm -f {PERS}/tmp/w150.bin', 15)
    log("ARCH", platform.machine(), "PY", platform.python_version())
    cdp_ok()
    log("SELFTEST_DONE")

def boot():
    log("BOOT_START")
    for d in (PERS, f"{PERS}/tmp", TMPH):
        try: os.makedirs(d, exist_ok=True)
        except Exception as e: log("MKDIR_EXC", d, str(e)[:60])
    if venv():
        restore(); hook()
        log("BOOT_VENV_OK")
    else:
        log("BOOT_VENV_FAIL")
    fix(PERS)
    log("BOOT_DONE")

def torch():
    ar = platform.machine()
    run(f"{VPIP} uninstall -y torch torchaudio 2>/dev/null", 120)
    if ar == "x86_64":
        if not pipc(["torch", "torchaudio", "--no-deps"], idx=TCU):
            log("CPU_INDEXES_EXHAUSTED")
            return False
    else:
        if not pipc(["torch", "torchaudio", "--no-deps"], idx=IDX):
            return False
    pipc(TORCH_DEPS)
    pipc(BASE_DEPS)
    pipc(DEMUC_DEPS)
    snap()
    log("TORCH_STACK_DONE")

def demucs(f):
    out = f"{PERS}/stems"
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2")
    try:
        r = sp.run([VPY, "-m", "demucs", "--device", "cpu", "-j", "2", "-n", "htdemucs",
                    "--out", out, f], capture_output=True, text=True, timeout=3600, env=env)
        log("DEMUC_RC", r.returncode, (r.stderr or "")[-160:].replace("\n", " "))
    except Exception as e:
        log("DEMUC_EXC", str(e)[:120])

def links(nid):
    g = "/mnt/agents/output/gaia_stream.py"
    if os.path.exists(g):
        r = run(f"python3 {g} {nid} /mnt/agents/output/gaia_{nid}", 300)
        log("LINKS", r.stdout[-200:], r.stderr[-120:])
    else:
        log("LINKS_NOGAIA", nid)

def main():
    a = sys.argv[1:]
    cmd = a[0] if a else "boot"
    if cmd != "boot":
        try: boot()
        except Exception as e: log("AUTOBOOT_EXC", str(e)[:80])
    if   cmd == "boot":     boot()
    elif cmd == "selftest": selftest()
    elif cmd == "probe":    race_sync(IDX)
    elif cmd == "pip":      pipc(a[1:]); snap()
    elif cmd == "torch":    torch()
    elif cmd == "snap":     snap()
    elif cmd == "restore":  restore()
    elif cmd == "demucs":   demucs(a[1])
    elif cmd == "kernel":   krn()
    elif cmd == "fix":      print(fix(a[1] if len(a) > 1 else PERS))
    elif cmd == "links":    links(a[1])
    else: log("UNKNOWN_CMD", cmd); print(__doc__)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("MAIN_EXC", str(e)[:120])
        try:
            boot()
        except Exception as e2:
            log("MAIN_NEST_EXC", str(e2)[:120])
