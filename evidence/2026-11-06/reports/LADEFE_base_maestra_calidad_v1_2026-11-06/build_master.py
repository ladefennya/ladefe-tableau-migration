import argparse,collections,csv,gzip,hashlib,json,math,re,sqlite3,statistics,unicodedata
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--sources',type=Path,required=True);P.add_argument('--repo',type=Path,required=True);P.add_argument('--out',type=Path,required=True);a=P.parse_args();a.out.mkdir(parents=True,exist_ok=True)
snapshot='2026-11-06'; dump=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'));hashj=lambda x:hashlib.sha256(dump(x).encode()).hexdigest()
def usable(x):
 s=' '.join(str(x or '').split()).lower();return any(c.isalnum() for c in s) and s not in ('','sin información','sin informacion','s/d','s/d.','no disponible','-','sin datos')
def norm(x):return ''.join(c for c in unicodedata.normalize('NFD',str(x or '').lower()) if unicodedata.category(c)!='Mn')
def num(x):
 try:return float(x) if math.isfinite(float(x)) else None
 except (TypeError,ValueError):return None
factors={'PORCENTAJE':100,'TASA_X_CIEN':100,'TASA_X_MIL':1000,'TASA_X_CIENMIL':100000,'TASA_X_MILLON':1000000,'RAZON_X_DIEZMIL':10000}
# No inference from names: ratios apply only to MAPA, as expressed in the Tableau XML.
def calc(r,unit):
 v=num(r['VALOR']);d=num(r['VALOR_AUXILIAR'])
 if r['TIPO_DE_DATO']!='MAPA':return v,'directo_fuente'
 if unit=='CANTIDAD':return v,'cantidad_mapa'
 if unit in factors and d not in (None,0):return v*factors[unit]/d,'ratio_mapa'
 return None,'no_calculable'
path=a.out/'base_maestra.sqlite'
if path.exists():raise SystemExit('Destino existente: usar un directorio nuevo para conservar la versión anterior.')
db=sqlite3.connect(path);db.execute('PRAGMA foreign_keys=ON')
db.executescript('''
CREATE TABLE snapshots(snapshot TEXT PRIMARY KEY, manifest_json TEXT NOT NULL);
CREATE TABLE boards(snapshot TEXT,workbook TEXT,board_id TEXT,metadata_json TEXT,source_sha256 TEXT,PRIMARY KEY(snapshot,workbook),FOREIGN KEY(snapshot) REFERENCES snapshots);
CREATE TABLE indicators(snapshot TEXT,workbook TEXT,indicator_id TEXT,metadata_json TEXT,PRIMARY KEY(snapshot,workbook,indicator_id),FOREIGN KEY(snapshot,workbook) REFERENCES boards);
CREATE TABLE groups_catalog(snapshot TEXT,workbook TEXT,group_id TEXT,metadata_json TEXT,PRIMARY KEY(snapshot,workbook,group_id),FOREIGN KEY(snapshot,workbook) REFERENCES boards);
CREATE TABLE observations(snapshot TEXT,observation_key TEXT,workbook TEXT,indicator_id TEXT,group_id TEXT,view_type TEXT,year INTEGER,period TEXT,geo_code TEXT,geo_name TEXT,value_raw REAL,auxiliary REAL,value_display REAL,calculation TEXT,dimensions_json TEXT,source_json TEXT,PRIMARY KEY(snapshot,observation_key),FOREIGN KEY(snapshot,workbook,indicator_id) REFERENCES indicators,FOREIGN KEY(snapshot,workbook,group_id) REFERENCES groups_catalog);
CREATE TABLE findings(id INTEGER PRIMARY KEY,rule TEXT,severity TEXT,workbook TEXT,indicator_id TEXT,observation_key TEXT,evidence_json TEXT);
CREATE TABLE source_payloads(row_hash TEXT PRIMARY KEY,payload_json TEXT NOT NULL);
CREATE TABLE source_records(snapshot TEXT,workbook TEXT,table_name TEXT,row_hash TEXT,PRIMARY KEY(snapshot,workbook,table_name,row_hash),FOREIGN KEY(row_hash) REFERENCES source_payloads);
CREATE INDEX observations_lookup ON observations(workbook,indicator_id,view_type,year,geo_code);
CREATE VIEW native_data AS SELECT o.*,json_extract(i.metadata_json,'$.INDICADOR_NOMBRE') indicator_name,json_extract(i.metadata_json,'$.INDICADOR_UNIDAD_MEDIDA_CODIGO') unit,json_extract(i.metadata_json,'$.INDICADOR_FORMULA') formula FROM observations o JOIN indicators i USING(snapshot,workbook,indicator_id);
''')
manifest={'snapshot':snapshot,'version':'1.0.0','scope':'71 workbooks inventariados; extracción pública del 6/11/2026','source_files':{},'policy':'originales preservados; sin correcciones estadísticas automáticas; claves por workbook y dimensiones; no agregación implícita'}
db.execute('INSERT INTO snapshots VALUES(?,?)',(snapshot,dump(manifest)))
findings=[];boardstats=[];changes=[];meta=[];allrows=[]
def finding(rule,severity,w,i=None,key=None,**e):findings.append(dict(rule=rule,severity=severity,workbook=w,indicator_id=i,observation_key=key,evidence_json=dump(e)))
catalog=json.loads((a.repo/'demo/catalog.json').read_text())['dashboards']
for item in catalog:
 w=item['workbook'];p=a.sources/(w+'.json.gz');raw=p.read_bytes();manifest['source_files'][p.name]=hashlib.sha256(raw).hexdigest();source=json.loads(gzip.decompress(raw));named=[r for r in source['Tableros'] if str(r['TABLERO_ID'])!='0'];assert len(named)==1
 board=named[0];bid=str(board['TABLERO_ID']);db.execute('INSERT INTO boards VALUES(?,?,?,?,?)',(snapshot,w,bid,dump(board),manifest['source_files'][p.name]))
 for t,rs in source.items():
  for r in rs:
   h=hashj(r);db.execute('INSERT OR IGNORE INTO source_payloads VALUES(?,?)',(h,dump(r)));db.execute('INSERT OR IGNORE INTO source_records VALUES(?,?,?,?)',(snapshot,w,t,h))
 inds={str(x['INDICADOR_ID']):x for x in source['Indicadores']};groups={str(x['GRUPO_INDICADOR_ID']):x for x in source['Grupos Indicadores']}
 for i,r in inds.items():db.execute('INSERT INTO indicators VALUES(?,?,?,?)',(snapshot,w,i,dump(r)))
 for g,r in groups.items():db.execute('INSERT INTO groups_catalog VALUES(?,?,?,?)',(snapshot,w,g,dump(r)))
 rows=[r for r in source['Datos'] if str(r['TABLERO_ID'])==bid and r['INDICADOR_ID'] not in (None,0,'0')];used={str(r['INDICADOR_ID']) for r in rows};views=collections.Counter();series=collections.defaultdict(list);maps=collections.defaultdict(list);distribution=collections.defaultdict(list)
 for i in used:
  r=inds[i];gused={str(x['GRUPO_INDICADOR_ID']) for x in rows if str(x['INDICADOR_ID'])==i}
  missing=[k for k in ['INDICADOR_DEFINICION','INDICADOR_DESC_METODOLOGICA','INDICADOR_FORMULA','INDICADOR_UNIDAD_MEDIDA_CODIGO'] if not usable(r.get(k))]
  for k in missing:finding('metadata_incompleta','advertencia',w,i,field=k)
  meta.append({'workbook':w,'indicator_id':i,'name':r['INDICADOR_NOMBRE'],'unit':r['INDICADOR_UNIDAD_MEDIDA_CODIGO'],'formula':r['INDICADOR_FORMULA'],'definition':r['INDICADOR_DEFINICION'],'methodology':r['INDICADOR_DESC_METODOLOGICA'],'sources':' | '.join(str(groups[g].get('GRUPO_INDICADOR_FUENTES') or '') for g in sorted(gused)),'missing_fields':' | '.join(missing)})
 for r in rows:
  i=str(r['INDICADOR_ID']);g=str(r['GRUPO_INDICADOR_ID']);unit=inds[i]['INDICADOR_UNIDAD_MEDIDA_CODIGO'];val,mode=calc(r,unit);views[r['TIPO_DE_DATO']]+=1
  dims={k:v for k,v in r.items() if k not in ['ID_DATO_SM','DATO_DE_SISTEMA','VALOR','VALOR_AUXILIAR']};key=hashj([w,dims]);rkey=key
  db.execute('INSERT INTO observations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(snapshot,key,w,i,g,r['TIPO_DE_DATO'],r['ANIO'],r['MES'],r['UNIDAD_GEOGRAFICA_CODIGO'],r['UNIDAD_GEOGRAFICA_NOMBRE'],r['VALOR'],r['VALOR_AUXILIAR'],val,mode,dump(dims),dump(r)))
  allrows.append((w,r,unit,val,key))
  if num(r['VALOR']) is None:finding('valor_no_finito','error',w,i,key)
  if mode=='no_calculable':finding('mapa_no_calculable','error',w,i,key,unit=unit,raw=r['VALOR'],aux=r['VALOR_AUXILIAR'])
  if mode=='ratio_mapa' and num(r['VALOR_AUXILIAR'])<0:finding('denominador_negativo','advertencia',w,i,key,aux=r['VALOR_AUXILIAR'])
  if unit=='PORCENTAJE' and val is not None and not 0<=val<=100:
   index=bool(re.search(r'base\s*100|indice|variacion',norm(inds[i]['INDICADOR_NOMBRE']+' '+str(inds[i]['INDICADOR_FORMULA'] or ''))))
   finding('indice_o_variacion_fuera_0_100' if index else 'porcentaje_fuera_0_100','informativo' if index else 'revision_tematica',w,i,key,value=val,name=inds[i]['INDICADOR_NOMBRE'],formula=inds[i]['INDICADOR_FORMULA'])
  if val is not None and val<0 and unit!='PORCENTAJE':finding('valor_negativo','revision_tematica',w,i,key,value=val,unit=unit)
  if r['ANIO'] and r['ANIO']>2026:finding('periodo_futuro','revision_tematica',w,i,key,year=r['ANIO'],name=inds[i]['INDICADOR_NOMBRE'])
  if r['TIPO_DE_DATO']=='SERIE_TEMPORAL':
   k=dump({k:v for k,v in dims.items() if k not in ['ANIO']});series[k].append((r['ANIO'],val,key,i))
  if r['TIPO_DE_DATO']=='MAPA':
   k=dump({k:v for k,v in dims.items() if k not in ['UNIDAD_GEOGRAFICA_CODIGO','UNIDAD_GEOGRAFICA_NOMBRE']});maps[k].append((r,val,key,i,unit))
  if r['TIPO_DE_DATO']=='DISTRIBUCION' and unit=='PORCENTAJE':
   k=dump({k:v for k,v in dims.items() if k not in ['MODALIDAD_APERTURA_NIVEL_1','MODALIDAD_APERTURA_NIVEL_2']});distribution[k].append((r,val,key,i))
 for k,s in series.items():
  s=sorted(s,key=lambda x:x[0] or 0)
  for prev,cur in zip(s,s[1:]):
   y0,v0,_,_=prev;y1,v1,key,i=cur
   if y0 and y1 and y1-y0==1 and v0 is not None and v1 is not None and abs(v0)>1e-9 and abs(v1-v0)/abs(v0)>0.5:finding('salto_interanual_mayor_50pct','revision_tematica',w,i,key,previous_year=y0,year=y1,previous=v0,current=v1,relative_change=(v1-v0)/abs(v0))
 # National reconciliation is a candidate only: additivity must be confirmed by the thematic team.
 map_checks=0
 for k,s in maps.items():
  if len({str(x[0]['UNIDAD_GEOGRAFICA_CODIGO']) for x in s})<24:finding('cobertura_mapa_menor_24','revision_tematica',w,s[0][3],None,jurisdictions=len({str(x[0]['UNIDAD_GEOGRAFICA_CODIGO']) for x in s}),dimensions=json.loads(k),reason='comprobar universo; ausencia no equivale a cero')
  countries=[x for x in s if str(x[0]['UNIDAD_GEOGRAFICA_CODIGO'])=='00'];provs=[x for x in s if str(x[0]['UNIDAD_GEOGRAFICA_CODIGO']) in {'02','06','10','14','18','22','26','30','34','38','42','46','50','54','58','62','66','70','74','78','82','86','90','94'}]
  if len(provs)==24 and len({x[0]['UNIDAD_GEOGRAFICA_CODIGO'] for x in provs})==24 and len(countries)==1:
   rr,v,key,i,unit=countries[0];map_checks+=1
   if unit=='CANTIDAD':expected=sum(x[1] for x in provs)
   elif unit in factors and all(num(x[0]['VALOR_AUXILIAR']) is not None for x in provs) and sum(x[0]['VALOR_AUXILIAR'] for x in provs)!=0:expected=sum(x[0]['VALOR'] for x in provs)/sum(x[0]['VALOR_AUXILIAR'] for x in provs)*factors[unit]
   else:continue
   if v is not None and not math.isclose(v,expected,rel_tol=1e-4,abs_tol=.02):finding('total_nacional_vs_24_provincias','revision_tematica',w,i,key,national=v,reconstructed=expected,unit=unit,reason='confirmar aditividad, universo y redondeo')
 dist_checks=0
 for k,s in distribution.items():
  if len(s)<2 or any(x[1] is None for x in s):continue
  dist_checks+=1;total=sum(x[1] for x in s)
  if abs(total-100)>max(.5,len(s)*.01):finding('categorias_no_suman_100','revision_tematica',w,s[0][3],None,sum=total,categories=len(s),dimensions=json.loads(k),reason='solo candidato: no se presume partición exhaustiva ni excluyente')
 # Compare selected old source values through the fields actually present in the old demo.
 old=json.loads((a.repo/'demo'/item['data']).read_text());mapping={'indicatorId':'INDICADOR_ID','groupId':'GRUPO_INDICADOR_ID','type':'TIPO_DE_DATO','year':'ANIO','month':'MES','geoCode':'UNIDAD_GEOGRAFICA_CODIGO','geoName':'UNIDAD_GEOGRAFICA_NOMBRE','subGeo':'SUB_UNIDAD_GEOGRAFICA','opening':'APERTURA_DESCRIPCION','level1':'APERTURA_NIVEL_1','mode1':'MODALIDAD_APERTURA_NIVEL_1','level2':'APERTURA_NIVEL_2','mode2':'MODALIDAD_APERTURA_NIVEL_2'}
 def oldkey(r):return dump([r.get(k) for k in mapping])
 previous={oldkey(r):r for r in old['rows']};current={dump([r.get(k) for k in mapping.values()]):r for r in rows}
 for k in sorted(previous.keys()|current.keys()):
  before=previous.get(k);after=current.get(k);status='alta' if before is None else 'baja' if after is None else 'modificacion' if (before.get('rawValue',before.get('value')),before.get('aux'))!=(after['VALOR'],after['VALOR_AUXILIAR']) else None
  if status:changes.append(dict(workbook=w,status=status,dimensions=k,before=dump(before),after=dump(after)))
 boardstats.append(dict(workbook=w,name=board['TABLERO_NOMBRE'],rows=len(rows),indicators=len(used),years=','.join(map(str,sorted({r['ANIO'] for r in rows if r['ANIO'] is not None}))),views=dump(views),national_comparisons=map_checks,distribution_comparisons=dist_checks))
for f in findings:db.execute('INSERT INTO findings(rule,severity,workbook,indicator_id,observation_key,evidence_json) VALUES(:rule,:severity,:workbook,:indicator_id,:observation_key,:evidence_json)',f)
db.execute('UPDATE snapshots SET manifest_json=?',(dump(manifest),));db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not db.execute('PRAGMA foreign_key_check').fetchall()
# Verify every normalized record reproduces the selected source JSON, without changing any raw value.
assert db.execute('SELECT COUNT(*) FROM observations').fetchone()[0]==sum(x['rows'] for x in boardstats)
for raw,v,aux in db.execute('SELECT source_json,value_raw,auxiliary FROM observations'):
 r=json.loads(raw);assert r['VALOR']==v and r['VALOR_AUXILIAR']==aux

def writecsv(name,rs):
 if not rs:return
 with (a.out/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
writecsv('hallazgos.csv',findings);writecsv('cambios_vs_github.csv',changes);writecsv('diccionario_indicadores.csv',meta);writecsv('cobertura_71.csv',boardstats)
(a.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));stats={'boards':len(boardstats),'observations':len(allrows),'indicator_links':len(meta),'findings_by_rule':dict(collections.Counter(x['rule'] for x in findings)),'findings_by_severity':dict(collections.Counter(x['severity'] for x in findings)),'changes':dict(collections.Counter(x['status'] for x in changes)),'changed_boards':len(set(x['workbook'] for x in changes)),'national_comparisons':sum(x['national_comparisons'] for x in boardstats),'distribution_comparisons':sum(x['distribution_comparisons'] for x in boardstats),'source_records':db.execute('SELECT COUNT(*) FROM source_records').fetchone()[0]};(a.out/'resumen.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2));db.close();print(json.dumps(stats,indent=2))
