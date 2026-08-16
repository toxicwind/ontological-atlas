#!/usr/bin/env python3
import sys, re, json, subprocess as sp

def luf(p):
    r = sp.run(["ffmpeg", "-hide_banner", "-nostats", "-i", p,
                "-af", "ebur128=peak=true", "-f", "null", "-"],
               capture_output=True, text=True, timeout=600)
    t = r.stderr
    i = t.rfind("Summary:")
    s = t[i:] if i >= 0 else t
    def g(pat, cast=float):
        m = re.search(pat, s)
        return cast(m.group(1)) if m else None
    return {
        "integrated_lufs": g(r"Integrated loudness:\s+I:\s+(-?[\d.]+)"),
        "lra_lu": g(r"Loudness range:\s+LRA:\s+(-?[\d.]+)"),
        "true_peak_dbtp": g(r"Peak:\s+(-?[\d.]+)"),
        "momentary_max": g(r"Momentary max:\s+M:\s+(-?[\d.]+)"),
        "shortterm_max": g(r"Short term max:\s+S:\s+(-?[\d.]+)"),
        "threshold_lufs": g(r"Threshold:\s+(-?[\d.]+)"),
    }

if __name__ == "__main__":
    try:
        print(json.dumps(luf(sys.argv[1]), indent=1))
    except Exception as e:
        print(json.dumps({"err": str(e)[:120]}))
