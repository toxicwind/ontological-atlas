import subprocess as sp,sys,platform,os
PIP="/tmp/av/bin/pip"
IDX=[("http://mirrors.cloud.aliyuncs.com/pypi/simple/","mirrors.cloud.aliyuncs.com"),
("https://mirrors.aliyun.com/pypi/simple/",None),
("http://mirrors.aliyun.com/pypi/simple/","mirrors.aliyun.com"),
("https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/",None),
("https://mirrors.ustc.edu.cn/pypi/web/simple/",None),
("https://pypi.org/simple/",None)]
TCU=[("http://mirrors.cloud.aliyuncs.com/pytorch-wheels/cpu","mirrors.cloud.aliyuncs.com"),
("https://mirrors.aliyun.com/pytorch-wheels/cpu",None),
("https://download.pytorch.org/whl/cpu",None)]
def pip(a,idx=IDX,t=1800):
 for u,th in idx:
  try:
   c=[PIP,"install","--no-input","--timeout","15"]+a+["-i",u]+(["--trusted-host",th] if th else [])
   r=sp.run(c,capture_output=True,text=True,timeout=t)
   if r.returncode==0:print("OK",u," ".join(a[:3]),flush=True);return True
   try:
    c2=c+["--no-cache-dir","--retries","1"]
    r2=sp.run(c2,capture_output=True,text=True,timeout=t)
    if r2.returncode==0:print("OK2",u," ".join(a[:3]),flush=True);return True
    print("FAIL",u,((r.stderr or "")+(r.stdout or ""))[-140:].replace("\n"," "),flush=True)
   except Exception as e2:print("NESTFAIL",u,str(e2)[:90],flush=True)
  except Exception as e:print("EXC",u,str(e)[:90],flush=True)
 return False
def main():
 ar=platform.machine()
 print("ARCH",ar,"PY",platform.python_version(),flush=True)
 pip(["install","-U","pip"])
 if ar=="x86_64":
  if not pip(["install","torch","torchaudio","--no-deps"],idx=TCU+IDX[3:]):
   pip(["install","torch","torchaudio","--no-deps"],idx=IDX)
 else:
  pip(["install","torch","torchaudio","--no-deps"],idx=IDX)
 pip(["install","filelock","typing-extensions","sympy","networkx","jinja2","fsspec","mpmath","setuptools"])
 pip(["install","librosa","soundfile"])
 pip(["install","demucs","lameenc","julius","einops","openunmix","dora-search","tqdm","pyyaml","diffq"])
 print("DONE",flush=True)
if __name__=="__main__":main()
