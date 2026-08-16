import sys,json,urllib.request as u
def cj(p="/json/version",port=9223):
  try:
    r=u.urlopen(f"http://127.0.0.1:{port}{p}",timeout=2);return json.loads(r.read())
  except Exception as e:return {"err":str(e)}
def ls():return cj("/json/list")
if __name__=="__main__":
  a=sys.argv[1] if len(sys.argv)>1 else "v"
  print(json.dumps(cj() if a=="v" else ls(),indent=1)[:2000])
