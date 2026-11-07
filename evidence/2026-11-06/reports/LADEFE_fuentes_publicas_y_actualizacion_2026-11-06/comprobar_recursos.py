import requests,concurrent.futures,json,hashlib,csv,io,zipfile
from pathlib import Path
O=Path('/tmp/ladefe-public-sources')
urls={
'educacion_2025':'https://www.argentina.gob.ar/sites/default/files/anuario_estadistico_2025.zip',
'defunciones_2024':'https://www.argentina.gob.ar/sites/default/files/2021/03/datos_sobre_defunciones_2024.csv',
'nacimientos_2024':'https://www.argentina.gob.ar/sites/default/files/2021/03/datos_sobre_nacidos_vivos_2024.csv',
'ispi_2024':'https://www.argentina.gob.ar/sites/default/files/ispi_2016_2024.xlsx',
'gpsdn_2024':'https://www.argentina.gob.ar/sites/default/files/gpsdn_2001_2024.xlsx',
'abandono':'https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_abandono_interanual.zip'}
def probe(k,u):
 try:
  r=requests.get(u,timeout=55);r.raise_for_status();p=O/(k+Path(u).suffix);p.write_bytes(r.content);x={'source':k,'url':u,'http':r.status_code,'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest()}
  if p.suffix in ('.zip','.xlsx'):
   z=zipfile.ZipFile(p);x['archive_files']=z.namelist()[:20]
  if p.suffix=='.csv':
   s=r.content.decode('utf-8-sig',errors='replace');x['sample']=s.splitlines()[:3];x['lines']=len(s.splitlines())
  return x
 except Exception as e:return {'source':k,'url':u,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:rs=list(ex.map(lambda x:probe(*x),urls.items()))
(O/'probe.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2));print(json.dumps(rs,ensure_ascii=False,indent=2))
