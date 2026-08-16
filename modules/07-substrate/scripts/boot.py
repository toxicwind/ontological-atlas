import os,subprocess as sp,shutil
def run(c,t=15):return sp.run(c,shell=True,capture_output=True,text=True,timeout=t)
def bt():
 os.makedirs("/tmp/h",exist_ok=True)
 for f in ["inst.py","kr.py","h.py","cdp.py"]:
  s=f"/mnt/agents/output/av/{f}"
  if os.path.exists(s):shutil.copy(s,"/tmp/h/"+f)
 if not os.path.exists("/tmp/av/bin/pip"):run("python3 -m venv /tmp/av",60)
 return run("ls /tmp/h").stdout
if __name__=="__main__":print(bt())
