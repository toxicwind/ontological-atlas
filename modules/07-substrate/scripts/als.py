import sys,gzip,json,re,xml.etree.ElementTree as ET
def rd(p):
 try:
  d=gzip.open(p,"rb").read()
 except OSError:
  d=open(p,"rb").read()
 try:return d.decode("utf-8")
 except UnicodeDecodeError:return d.decode("latin-1")
def dec(p,out=None):
 x=rd(p)
 try:
  r=ET.fromstring(x)
  def ind(e,l=0):
   for i in e:i.text=(i.text or "").strip()or None;ind(i,l+1)
   if len(e):e.text="\n"+"  "*(l+1);e[-1].tail=(e[-1].tail or "")+""
  ind(r)
  px=ET.tostring(r,encoding="unicode")
 except ET.ParseError:px=x
 o=out or re.sub(r"\.als$","",p)+".xml"
 open(o,"w").write(px)
 return o
def sumz(p):
 x=rd(p)
 d={"major":None,"minor":None,"creator":None,"tracks":[],"devices":set(),"plugins":set(),"tempo":None}
 m=re.search(r'<Ableton[^>]*MajorVersion="([^"]*)"[^>]*MinorVersion="([^"]*)"[^>]*Creator="([^"]*)"',x)
 if m:d["major"],d["minor"],d["creator"]=m.groups()
 d["tracks"]=re.findall(r'<(?:AudioTrack|MidiTrack|ReturnTrack|GroupTrack)\b[^>]*?Id="\d+"',x).__len__().__str__() and re.findall(r'<Name Value="([^"]+)"',x)[:40]
 d["devices"]=sorted(set(re.findall(r'<([A-Z][A-Za-z0-9]+) Id="\d+"',x)))[:60]
 d["plugins"]=sorted(set(re.findall(r'(?:PluginName|Name) Value="((?:Serum|Vital|Massive|ShaperBox|OTT|Multipass|FabFilter|Kontakt)[^"]*)"',x)))
 t=re.search(r'<Tempo[^>]*>\s*<Manual Value="([\d.]+)"',x)
 if t:d["tempo"]=float(t.group(1))
 return d
if __name__=="__main__":
 a=sys.argv
 if len(a)>2 and a[1]=="sum":print(json.dumps(sumz(a[2]),indent=1,default=str))
 elif len(a)>2:print(dec(a[2],a[3] if len(a)>3 else None))
 else:print("als.py dec <in.als> [out.xml] | als.py sum <in.als>")
