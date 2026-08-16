import sys,json,urllib.request as u
def gj(p,mt="GET"):
 try:
  q=u.Request("http://127.0.0.1:8888"+p,method=mt)
  r=u.urlopen(q,timeout=3);return json.loads(r.read())
 except Exception as e:
  try:
   q=u.Request("http://127.0.0.1:9223"+p,method=mt)
   r=u.urlopen(q,timeout=3);return json.loads(r.read())
  except Exception as e2:return {"err":f"{e}|{e2}"}
def rst():
 ks=gj("/api/kernels")
 if isinstance(ks,list) and ks:
  return gj(f"/api/kernels/{ks[0]['id']}/restart","POST")
 return ks
if __name__=="__main__":print(json.dumps(rst())[:800])
