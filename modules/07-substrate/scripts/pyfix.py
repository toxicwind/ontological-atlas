#!/usr/bin/env python3
import sys, io, re, tokenize, subprocess as sp

def rd(p):
    b = open(p, "rb").read()
    b = b.replace(b"\x00", b"")
    if b.startswith(b"\xef\xbb\xbf"):
        b = b[3:]
    for e in ("utf-8", "latin-1"):
        try:
            return b.decode(e)
        except Exception:
            pass
    return b.decode("utf-8", "replace")

def st(s):
    try:
        out = []
        for t in tokenize.generate_tokens(io.StringIO(s).readline):
            if t.type == tokenize.COMMENT:
                continue
            out.append(t)
        return tokenize.untokenize(out)
    except Exception:
        return re.sub(r"(?m)^[ \t]*#.*$", "", s)

def fx(s):
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\t", "    ")
    s = re.sub(r"[ \t]+\n", "\n", s)
    try:
        compile(s, "<fx>", "exec")
        return s, 0
    except SyntaxError:
        pass
    s2 = st(s)
    try:
        compile(s2, "<fx>", "exec")
        return s2, 1
    except SyntaxError:
        pass
    lines = s2.split("\n")
    bal = 0
    for i, ln in enumerate(lines):
        bal += ln.count("(") - ln.count(")") + ln.count("[") - ln.count("]") + ln.count("{") - ln.count("}")
        if bal < 0:
            lines[i] = re.sub(r"[\)\]\}]+$", "", ln)
            bal = 0
    s3 = "\n".join(lines)
    if bal > 0:
        s3 += "\n" + ")" * bal
    try:
        compile(s3, "<fx>", "exec")
        return s3, 2
    except SyntaxError as e:
        return s3, 10 + (e.lineno or 0)

def main(p, write=True):
    s = rd(p)
    r, code = fx(s)
    if write and r != s:
        open(p, "w", encoding="utf-8").write(r)
    print(f"{p} fix_level={code}")
    return 0 if code < 10 else 1

if __name__ == "__main__":
    p = sys.argv[1]
    chk = "--check" in sys.argv
    try:
        sys.exit(main(p, write=not chk))
    except Exception as e:
        print(f"{p} PYFIX_EXC {str(e)[:80]}")
        sys.exit(2)
