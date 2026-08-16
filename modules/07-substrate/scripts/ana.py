#!/usr/bin/env python3
import sys, json, time
T0 = time.time()

def ana(p, sr=22050):
    import numpy as np, librosa
    y, s = librosa.load(p, sr=sr, mono=True)
    d = float(librosa.get_duration(y=y, sr=s))
    tm = librosa.beat.tempo(y=y, sr=s)
    r = librosa.feature.rms(y=y)[0]
    c = librosa.feature.spectral_centroid(y=y, sr=s)[0]
    z = librosa.feature.zero_crossing_rate(y)[0]
    o = librosa.onset.onset_strength(y=y, sr=s)
    h, pc = librosa.effects.hpss(y)
    def fl(x):
        return float(np.mean(x))
    return {
        "file": p, "sr": s, "dur_s": round(d, 2),
        "bpm": round(float(tm[0]) if len(tm) else 0.0, 1),
        "rms_mean": round(fl(r), 5), "rms_max": round(float(np.max(r)), 5),
        "centroid_hz": round(fl(c), 1), "zcr": round(fl(z), 5),
        "onset_mean": round(fl(o), 3),
        "harmonic_rms": round(float(np.sqrt(np.mean(h**2))), 5),
        "percussive_rms": round(float(np.sqrt(np.mean(pc**2))), 5),
        "elapsed_s": round(time.time() - T0, 2),
    }

if __name__ == "__main__":
    try:
        print(json.dumps(ana(sys.argv[1]), indent=1))
    except Exception as e:
        try:
            print(json.dumps(ana(sys.argv[1], sr=11025), indent=1))
        except Exception as e2:
            print(json.dumps({"err": f"{str(e)[:80]}|{str(e2)[:80]}"}))
