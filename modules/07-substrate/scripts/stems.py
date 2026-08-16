#!/usr/bin/env python3
import sys, os, time, subprocess as sp
T0 = time.time()
def log(*a):
    print(f"[+{time.time()-T0:8.3f}s]", *a, flush=True)

VPY = "/tmp/av/bin/python"
OUT = "/mnt/agents/output/av/stems"

def stems(f, model="htdemucs", jobs="2"):
    os.makedirs(OUT, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", TORCH_HOME="/mnt/agents/output/av/torch_cache")
    c = [VPY, "-m", "demucs", "--device", "cpu", "-j", jobs, "-n", model, "--out", OUT, f]
    try:
        r = sp.run(c, capture_output=True, text=True, timeout=7200, env=env)
        log("RC", r.returncode)
        for ln in (r.stderr or "").splitlines()[-6:]:
            log("D", ln[:140])
    except Exception as e:
        log("EXC", str(e)[:120])
        try:
            r2 = sp.run(c + ["--two-stems", "vocals"], capture_output=True, text=True, timeout=3600, env=env)
            log("RC2", r2.returncode)
        except Exception as e2:
            log("EXC2", str(e2)[:120])
    q = sp.run(f'find {OUT} -name "*.wav" -newer {OUT} -printf "%s %p\\n" 2>/dev/null | sort -rn | awk "{{printf \\"%.1fMB %s\\n\\",\\$1/1048576,\\$2}}"',
               shell=True, capture_output=True, text=True, timeout=30)
    print(q.stdout)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        stems(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "htdemucs")
    else:
        print("stems.py <audio> [model]")
