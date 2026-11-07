#!/usr/bin/env python3
"""Official interannual dropout workbook -> candidate native observations.
No network writes, no changes to the reference database. Python + openpyxl.
"""
import argparse,csv,hashlib,io,json,math,re,sqlite3,unicodedata,zipfile
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
SOURCE='https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_abandono_interanual.zip'
WB='3_3fMatrculaIEPromocinyabandono'
GEO={'total pais':('00','national'),'buenos aires':('06','province'),'conurbano':('06-CON','subprovince'),'resto de bs as':('06-REST','subprovince'),'ciudad de buenos aires':('02','province'),'catamarca':('10','province'),'chaco':('22','province'),'chubut':('26','province'),'cordoba':('14','province'),'corrientes':('18','province'),'entre rios':('30','province'),'formosa':('34','province'),'jujuy':('38','province'),'la pampa':('42','province'),'la rioja':('46','province'),'mendoza':('50','province'),'misiones':('54','province'),'neuquen':('58','province'),'rio negro':('62','province'),'salta':('66','province'),'san juan':('70','province'),'san luis':('74','province'),'santa cruz':('78','province'),'santa fe':('82','province'),'santiago del estero':('86','province'),'tierra del fuego':('94','province'),'tucuman':('90','province')}
def require(condition,message):
 if not condition:raise ValueError(message)
def normalized(s):return ' '.join(''.join(c for c in unicodedata.normalize('NFD',str(s or '').lower()) if unicodedata.category(c)!='Mn').split())
def rounded(value,decimals=1):
 return Decimal(str(value)).quantize(Decimal(1).scaleb(-decimals),rounding=ROUND_HALF_UP)
def format_decimals(number_format):
 match=re.fullmatch(r'0(?:\.(0+))?',number_format or 'General')
 return len(match.group(1) or '') if match else None
def map_reference(iid,r):
 label=normalized(r.get('MODALIDAD_APERTURA_NIVEL_1'))
 if iid=='384':
  levels={'tasa de abandono interanual del nivel primario':'primary','tasa de abandono interanual del nivel secundario':'secondary'}
  require(label in levels,('Unknown national series modality',label));return levels[label],'total'
 require(iid in ['380','381','382','383'],('Unknown reference indicator',iid))
 level='primary' if iid in ['380','381'] else 'secondary'
 if iid in ['381','383']:return level,'total'
 if label=='total':return level,'total'
 primary={'1ero':'1','2do':'2','3ero':'3','4to':'4','5to':'5','6to':'6','7mo (e.e - 7-5)':'7'}
 secondary={'7mo (e.e - 6-6)':'7','8vo':'8','9no':'9','10mo':'10','11avo':'11','12avo':'12'}
 grades=primary if level=='primary' else secondary
 require(label in grades,('Unknown grade category',iid,label));return level,grades[label]
def stable_key(r):
 dims=[r[k] for k in ['metric','period_start','period_end','geo_code','education_structure','level','grade_system']]
 return hashlib.sha256(json.dumps(dims,separators=(',',':')).encode()).hexdigest()
def extract(path):
 data=Path(path).read_bytes();sha=hashlib.sha256(data).hexdigest();z=zipfile.ZipFile(io.BytesIO(data));members=[n for n in z.namelist() if n.endswith('.xlsx') and 'división político-territorial' in n];require(len(members)==1,'Expected one territorial workbook')
 import openpyxl
 member=members[0];member_bytes=z.read(member);member_sha=hashlib.sha256(member_bytes).hexdigest();wb=openpyxl.load_workbook(io.BytesIO(member_bytes),read_only=True,data_only=True)
 limitations='\n'.join(str(v) for row in wb['Limitaciones'].values for v in row if v)
 observations=[];notes={};sheets=[]
 for sn in wb.sheetnames:
  if not re.fullmatch(r'\d{4}-\d{4}',sn):continue
  ys,ye=map(int,sn.split('-'));require(ye==ys+1,('Non-consecutive school-year period',sn))
  sheet=wb[sn];cells=list(sheet.iter_rows());rows=[tuple(c.value for c in row) for row in cells]
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
    raw=row[ci];number_format=cells[ri-1][ci].number_format;decimals=format_decimals(number_format);nonapp=(structure=='6-6' and level=='primary' and grade=='7') or (structure=='7-5' and level=='secondary' and grade=='7')
    if raw is not None:require('%' not in (number_format or ''),(sn,ri,ci,'Percentage cell format changed: percent scale requires review'))
    if raw is not None and (not isinstance(raw,(int,float)) or not math.isfinite(raw)):raise ValueError((sn,ri,ci,'Non numeric cell'))
    # Structural inapplicability is an explicit dimension, not an imputed zero.
    if nonapp and raw is not None:raise ValueError((sn,ri,ci,'Non-applicable cell unexpectedly populated'))
    effective_structure='7-5' if geo[1]=='national' and level=='primary' and grade=='7' else '6-6' if geo[1]=='national' and level=='secondary' and grade=='7' else structure
    r={'metric':'interannual_dropout_rate','period_start':ys,'period_end':ye,'period_label':sn,'geo_code':geo[0],'geo_level':geo[1],'geo_name':str(row[0]).strip(),'education_structure':effective_structure,'geo_education_structure':structure,'level':level,'grade_system':grade,'unit':'percent','value':raw,'source_number_format':number_format,'source_display_decimals':decimals,'source_display_value':str(rounded(raw,decimals)) if raw is not None and decimals is not None else None,'cell_status':'not_applicable' if nonapp else 'missing' if raw is None else 'observed','source_url':SOURCE,'source_sha256':sha,'source_member':member,'source_member_sha256':member_sha,'source_sheet':sn,'source_row':ri,'source_column':ci+1,'release_status':'candidate_not_approved','aggregation':'published_value_do_not_average_or_sum'}
    r['observation_key']=stable_key(r);observations.append(r)
  require(len(matched)==27 and len(set(matched))==27,(sn,'Unexpected geography coverage',matched))
  last_geo_row=max(r['source_row'] for r in observations if r['source_sheet']==sn)
  notes[sn]=[str(row[0]) for row in rows[last_geo_row:] if row[0]];sheets.append(sn)
 require(bool(sheets),'No school-year sheets found')
 require(len({r['observation_key'] for r in observations})==len(observations),'Duplicate observation key')
 return observations,{'source_sha256':sha,'source_member_sha256':member_sha,'source_url':SOURCE,'source_member':member,'limitations':limitations,'sheet_notes':notes,'sheets':sheets,'selection':'división político-territorial; never merge with estructura nacional homogénea workbook','rounding_policy':'Decimal ROUND_HALF_UP; source display formatting retained; no epsilon tolerance','period_convention':'explicit start and end school years; no assumption that a scalar year is the final year'}
def reconcile(observations,db_path):
 db=sqlite3.connect('file:'+str(Path(db_path).resolve())+'?mode=ro',uri=True);rows=db.execute('SELECT indicator_id,source_json,observation_key FROM observations WHERE workbook=? AND indicator_id IN (?,?,?,?,?)',(WB,'380','381','382','383','384')).fetchall();db.close()
 lookup={(r['period_start'],r['geo_code'],r['level'],r['grade_system']):r for r in observations};require(len(lookup)==len(observations),'Ambiguous candidate lookup across education structures')
 db=sqlite3.connect('file:'+str(Path(db_path).resolve())+'?mode=ro',uri=True)
 try:
  meta_row=db.execute('SELECT metadata_json FROM indicators WHERE workbook=? AND indicator_id=?',(WB,'384')).fetchone()
 except sqlite3.OperationalError:meta_row=None
 db.close();national_metadata=normalized(json.loads(meta_row[0]).get('INDICADOR_DESC_METODOLOGICA')) if meta_row else '';out=[]
 for iid,payload,refkey in rows:
  r=json.loads(payload);level,grade=map_reference(iid,r);raw_geo=r.get('UNIDAD_GEOGRAFICA_CODIGO');geo_name=normalized(r.get('UNIDAD_GEOGRAFICA_NOMBRE'))
  expected_view='MAPA' if iid in ['381','383'] else 'APERTURA' if iid in ['380','382'] else 'SERIE_TEMPORAL'
  require(r['TIPO_DE_DATO']==expected_view,('Unexpected reference view',iid,r['TIPO_DE_DATO']))
  scope_evidence='explicit_source_geography'
  if raw_geo is None:
   require(iid=='384' and not geo_name and 'total del pais' in national_metadata,('Absent geographic scope not justified',iid));geo='00';scope_evidence='curated_indicator_384_methodology_total_del_pais;reference_row_geo_null'
  else:geo=str(raw_geo)
  require(geo in {v[0] for v in GEO.values() if v[1]=='province'} if expected_view=='MAPA' else geo=='00',('Unexpected geographic scope',iid,geo))
  year=r['ANIO'];require(type(year) is int,('Non-integer reference year',iid,year));source=lookup.get((year,geo,level,grade));description=str(r.get('APERTURA_DESCRIPCION') or '');label_period=re.search(r'(\d{4})\s*[/–-]\s*(\d{4})',description);conflict=bool(label_period and tuple(map(int,label_period.groups()))!=(year,year+1))
  raw=r['VALOR'];aux=r['VALOR_AUXILIAR'];reference_decimal=Decimal(str(raw))/Decimal(str(aux))*Decimal(100) if r['TIPO_DE_DATO']=='MAPA' and aux not in (None,0) else Decimal(str(raw))
  require(reference_decimal==rounded(reference_decimal),('Reference no longer has declared one-decimal precision',iid,str(reference_decimal)));reference=float(reference_decimal)
  value=source['value'] if source else None;delta=None if value is None else value-reference
  equal=value is not None and rounded(value)==rounded(reference)
  displayed=source.get('source_display_value') if source else None
  display_equal=displayed is not None and rounded(displayed)==rounded(reference)
  status='blocked_temporal_label_conflict' if conflict else 'matched_at_one_decimal' if equal else 'compatible_with_double_rounding' if display_equal else 'different_value' if source else 'no_source_match'
  x={'indicator_id':iid,'reference_key':refkey,'year_field':year,'explicit_label':description,'native_period':source['period_label'] if source else None,'geo_code':geo,'geographic_scope_evidence':scope_evidence,'level':level,'grade_system':grade,'tableau_value':reference,'official_value':value,'official_cell_number_format':source.get('source_number_format') if source else None,'official_display_value':displayed,'official_raw_rounded_1dp':str(rounded(value)) if value is not None else None,'official_display_rounded_1dp':str(rounded(displayed)) if displayed is not None else None,'reference_rounded_1dp':str(rounded(reference)),'rounding_policy':'decimal_HALF_UP;compare_raw_and_display_separately','delta_pp':delta,'matches_one_decimal':equal,'matches_after_official_display_rounding':display_equal,'period_label_conflict':conflict,'status':status,'native_key':source['observation_key'] if source else None}
  if label_period:
   alt=lookup.get((int(label_period.group(1)),geo,level,grade));x['value_for_explicit_label_period']=alt['value'] if alt else None;x['matches_explicit_label_period']=alt is not None and alt['value'] is not None and rounded(alt['value'])==rounded(reference)
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
 (a.out/'native_candidate.json').write_text(json.dumps({'schema_version':'1.1.0','metric':'interannual_dropout_rate','metadata':meta,'observations':rs},ensure_ascii=False,indent=2));writecsv(a.out/'native_candidate.csv',rs)
 if comp:(a.out/'reconciliation.json').write_text(json.dumps(comp,ensure_ascii=False,indent=2));writecsv(a.out/'reconciliation.csv',comp)
 summary={'observations':len(rs),'observed_cells':sum(r['cell_status']=='observed' for r in rs),'not_applicable':sum(r['cell_status']=='not_applicable' for r in rs),'missing':sum(r['cell_status']=='missing' for r in rs),'negative_values':sum(r['value'] is not None and r['value']<0 for r in rs),'periods':len(meta['sheets']),'geo_units_per_period':27,'reference_rows':len(comp),'matches_at_one_decimal':sum(r['matches_one_decimal'] for r in comp),'compatible_after_double_rounding':sum(r['status']=='compatible_with_double_rounding' for r in comp),'label_conflicts':sum(r['period_label_conflict'] for r in comp),'status_counts':{k:sum(r['status']==k for r in comp) for k in set(r['status'] for r in comp)},'source_sha256':meta['source_sha256'],'reference_sha256':hashlib.sha256(a.reference_db.read_bytes()).hexdigest() if a.reference_db else None,'release_status':'candidate_not_approved'}
 (a.out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(a.out/'reconciliation_summary.json').write_text(json.dumps({k:v for k,v in summary.items() if k in ['reference_rows','matches_at_one_decimal','label_conflicts','compatible_after_double_rounding','status_counts','source_sha256','release_status']},ensure_ascii=False,indent=2));manifest={'adapter_schema_version':'1.1.0','adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_member_sha256':meta['source_member_sha256'],'source_sha256':meta['source_sha256'],'reference_sha256':summary['reference_sha256'],'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(a.out.iterdir()) if p.is_file()}};(a.out/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
