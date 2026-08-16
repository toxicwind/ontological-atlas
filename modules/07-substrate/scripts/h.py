import sys,os,subprocess as sp
def run(c,t=2):return sp.run(c,shell=True,capture_output=True,text=True,timeout=t)
def fix(p):run(f"chmod -R 777 {p} 2>/dev/null;chown -R $(whoami) {p} 2>/dev/null;ls -la {p}")
if __name__=="__main__":fix(sys.argv[1])
