#!/usr/bin/env python3
"""Official interannual dropout workbook -> candidate native observations.
No network writes, no changes to the reference database. Python + openpyxl.
"""
import argparse,csv,hashlib,io,json,math,re,sqlite3,unicodedata,zipfile
from pathlib import Path
SOURCE='https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_abandono_interanual.zip'
WB='3_3fMatrculaIEPromocinyabandono'
GEO={'total pais':('00','national'),'buenos aires':('06','province'),'conurbano':('06-CON','subprovince'),'resto de bs as':('06-REST','subprovince'),'ciudad de buenos aires':('02','province'),'catamarca':('10','province'),'chaco':('22','province'),'chubut':('26','province'),'cordoba':('14','province'),'corrientes':('18','province'),'entre rios':('30','province'),'formosa':('34','province'),'jujuy':('38','province'),'la pampa':('42','province'),'la rioja':('46','province'),'mendoza':('50','province'),'misiones':('54','province'),'neuquen':('58','province'),'rio negro':('62','province'),'salta':('66','province'),'san juan':('70','province'),'san luis':('74','province'),'santa cruz':('78','province'),'santa fe':('82','province'),'santiago del estero':('86','province'),'tierra del fuego':('94','province'),'tucuman':('90','province')}
def require(condition,message):
 if not condition:raise ValueError(message)
def normalized(s):return ' '.join(''.join(c for c in unicodedata.normalize('NFD',str(s or '').lower()) if unicodedata.category(c)!='Mn').split())
def stable_key(r):
 dims=[r[k] for k in ['metric','period_start','period_end','geo_code','education_structure','level','grade_system']]
 return hashlib.sha256(json.dumps(dims,separators=(',',':')).encode()).hexdigest()
def extract(path):
 data=Path(path).read_bytes();sha=hashlib.sha256(data).hexdigest();z=zipfile.ZipFile(io.BytesIO(data));members=[n for n in z.namelist() if n.endswith('.xlsx') and 'división político-territorial' in n];require(len(members)==1,'Expected one territorial workbook')
 import openpyxl
 member=members[0];wb=openpyxl.load_workbook(io.BytesIO(z.read(member)),read_only=True,data_only=True)
 limitations='\n'.join(str(v) for row in wb['Limitaciones'].values for v in row if v)
 observations=[];notes={};sheets=[]
 for sn in wb.sheetnames:
  if not re.fullmatch(r'\d{4}-\d{4}',sn):continue
  ys,ye=map(int,sn.split('-'));require(ye==ys+1,('Non-consecutive school-year period',sn))
  sheet=wb[sn];rows=list(sheet.values)
  # Explicit contract; fail on layout change, rather than silently selecting wrong columns.
  headers=[k for k,row in enumerate(rows) if normalized(row[0]).startswith('division') and row[2]=='Primaria' and row[10]=='Secundaria']
  require(len(headers)==1,(sn,'Unexpected header'))
  header=headers[0];require(rows[header+1][2]=='Total' and rows[header+1][10]=='Total',(sn,'Unexpected total column headers'))
  columns=[(2,'primary','total')]+[(c,'primary',str(c-2)) for c in range(3,10)]+[(10,'secondary','total')]+[(c,'secondary',str(c-4)) for c in range(11,17)]
  matched=[]
  for ri,row in enumerate(rows,1):
   label=normalized(row[0]);geo=GEO.get(label)
   if geo is None:
    if len(row)>2 and row[1] in ('6-6','7-5') and isinstance(row[2],(int,float)):raise ValueError((sn,ri,'Unrecognized geography',row[0]))
    continue
   matched.append(geo[0]);structure=str(row[1]).strip() if row[1] else 'mixed';require(structure in ('6-6','7-5','mixed'),(sn,ri,'Unknown education structure',structure))
   for ci,level,grade in columns:
    raw=row[ci];nonapp=(structure=='6-6' and level=='primary' and grade=='7') or (structure=='7-5' and level=='secondary' and grade=='7')
    if raw is not None and (not isinstance(raw,(int,float)) or not math.isfinite(raw)):raise ValueError((sn,ri,ci,'Non numeric cell'))
    # Structural inapplicability is an explicit dimension, not an imputed zero.
    if nonapp and raw is not None:raise ValueError((sn,ri,ci,'Non-applicable cell unexpectedly populated'))
    r={'metric':'interannual_dropout_rate','period_start':ys,'period_end':ye,'period_label':sn,'geo_code':geo[0],'geo_level':geo[1],'geo_name':str(row[0]).strip(),'education_structure':structure,'level':level,'grade_system':grade,'unit':'percent','value':raw,'cell_status':'not_applicable' if nonapp else 'missing' if raw is None else 'observed','source_url':SOURCE,'source_sha256':sha,'source_member':member,'source_sheet':sn,'source_row':ri,'source_column':ci+1,'release_status':'candidate_not_approved','aggregation':'published_value_do_not_average_or_sum'}
    r['observation_key']=stable_key(r);observations.append(r)
  require(len(matched)==27 and len(set(matched))==27,(sn,'Unexpected geography coverage',matched))
  last_geo_row=max(r['source_row'] for r in observations if r['source_sheet']==sn)
  notes[sn]=[str(row[0]) for row in rows[last_geo_row:] if row[0]];sheets.append(sn)
 require(bool(sheets),'No school-year sheets found')
 require(len({r['observation_key'] for r in observations})==len(observations),'Duplicate observation key')
 return observations,{'source_sha256':sha,'source_url':SOURCE,'source_member':member,'limitations':limitations,'sheet_notes':notes,'sheets':sheets,'selection':'división político-territorial; never merge with estructura nacional homogénea workbook','period_convention':'explicit start and end school years; no assumption that a scalar year is the final year'}
def reconcile(observations,db_path):
 db=sqlite3.connect('file:'+str(Path(db_path).resolve())+'?mode=ro',uri=True);rows=db.execute('SELECT indicator_id,source_json,observation_key FROM observations WHERE workbook=? AND indicator_id IN (?,?,?,?,?)',(WB,'380','381','382','383','384')).fetchall();db.close()
 lookup={(r['period_start'],r['geo_code'],r['level'],r['grade_system']):r for r in observations};out=[]
 for iid,payload,refkey in rows:
  r=json.loads(payload);level='primary' if iid in ['380','381'] else 'secondary' if iid in ['382','383'] else 'primary' if 'primari' in normalized(r['MODALIDAD_APERTURA_NIVEL_1']) else 'secondary';geo=str(r['UNIDAD_GEOGRAFICA_CODIGO'] or '00');grade='total'
  if iid in ['380','382']:
   label=str(r['MODALIDAD_APERTURA_NIVEL_1']);m=re.match(r'(\d+)',label);grade=m.group(1) if m else 'total'
  year=r['ANIO'];source=lookup.get((year,geo,level,grade));description=str(r.get('APERTURA_DESCRIPCION') or '');label_period=re.search(r'(\d{4})\s*[/–-]\s*(\d{4})',description);conflict=bool(label_period and tuple(map(int,label_period.groups()))!=(year,year+1))
  raw=r['VALOR'];aux=r['VALOR_AUXILIAR'];reference=raw/aux*100 if r['TIPO_DE_DATO']=='MAPA' and aux not in (None,0) else raw
  value=source['value'] if source else None;delta=None if value is None else value-reference
  # Half of the final displayed decimal interval; the original Tableau records have one decimal.
  equal=value is not None and abs(delta)<=.0500000001
  x={'indicator_id':iid,'reference_key':refkey,'year_field':year,'explicit_label':description,'native_period':source['period_label'] if source else None,'geo_code':geo,'level':level,'grade_system':grade,'tableau_value':reference,'official_value':value,'delta_pp':delta,'matches_one_decimal':equal,'period_label_conflict':conflict,'status':'blocked_temporal_label_conflict' if conflict else 'matched_at_one_decimal' if equal else 'different_value' if source else 'no_source_match','native_key':source['observation_key'] if source else None}
  if label_period:
   alt=lookup.get((int(label_period.group(1)),geo,level,grade));x['value_for_explicit_label_period']=alt['value'] if alt else None
  out.append(x)
 return out
def writecsv(path,rows):
 fields=list(dict.fromkeys(k for row in rows for k in row))
 with path.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-zip',type=Path,required=True);p.add_argument('--reference-db',type=Path);p.add_argument('--expected-sha256');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists() and any(a.out.iterdir()):raise SystemExit('Output must be new or empty: preserve previous versions')
 if a.expected_sha256 and hashlib.sha256(a.source_zip.read_bytes()).hexdigest()!=a.expected_sha256:raise SystemExit('Source SHA-256 does not match the approved/pinned file')
 a.out.mkdir(parents=True,exist_ok=True);rs,meta=extract(a.source_zip);comp=reconcile(rs,a.reference_db) if a.reference_db else []
 (a.out/'native_candidate.json').write_text(json.dumps({'schema_version':'1.0.0','metric':'interannual_dropout_rate','metadata':meta,'observations':rs},ensure_ascii=False,indent=2));writecsv(a.out/'native_candidate.csv',rs)
 if comp:(a.out/'reconciliation.json').write_text(json.dumps(comp,ensure_ascii=False,indent=2));writecsv(a.out/'reconciliation.csv',comp)
 summary={'observations':len(rs),'observed_cells':sum(r['cell_status']=='observed' for r in rs),'not_applicable':sum(r['cell_status']=='not_applicable' for r in rs),'missing':sum(r['cell_status']=='missing' for r in rs),'negative_values':sum(r['value'] is not None and r['value']<0 for r in rs),'periods':len(meta['sheets']),'geo_units_per_period':27,'reference_rows':len(comp),'matches_at_one_decimal':sum(r['matches_one_decimal'] for r in comp),'label_conflicts':sum(r['period_label_conflict'] for r in comp),'status_counts':{k:sum(r['status']==k for r in comp) for k in set(r['status'] for r in comp)},'source_sha256':meta['source_sha256'],'release_status':'candidate_not_approved'}
 (a.out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(a.out/'reconciliation_summary.json').write_text(json.dumps({k:v for k,v in summary.items() if k in ['reference_rows','matches_at_one_decimal','label_conflicts','status_counts','source_sha256','release_status']},ensure_ascii=False,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
