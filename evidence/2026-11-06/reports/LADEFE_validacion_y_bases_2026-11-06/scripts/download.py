import concurrent.futures,csv,requests,zipfile,hashlib,json,time
from pathlib import Path
root=Path('/tmp/ladefe-validation'); dest=root/'raw';dest.mkdir(exist_ok=True)
boards=list(csv.DictReader(open('/tmp/ladefe-check/config/all_workbooks.csv',encoding='utf-8-sig')))
def run(b):
 w=b['workbook'];p=dest/(w+'.twbx')
 try:
  if not p.exists():
   r=requests.get('https://public.tableau.com/workbooks/'+w+'.twb',timeout=60);r.raise_for_status();p.write_bytes(r.content)
  z=zipfile.ZipFile(p); target=root/'unpacked'/w;target.mkdir(parents=True,exist_ok=True)
  for i in z.infolist():
   if i.filename.endswith(('.hyper','.twb')):
    (target/Path(i.filename).name).write_bytes(z.read(i))
  return dict(workbook=w,status='ok',bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 except Exception as e:return dict(workbook=w,status='error',error=str(e))
res=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for r in ex.map(run,boards):res.append(r);print(len(res),r['status'],r['workbook'],flush=True)
(root/'downloads.json').write_text(json.dumps(res,indent=2));print('DONE',flush=True)
