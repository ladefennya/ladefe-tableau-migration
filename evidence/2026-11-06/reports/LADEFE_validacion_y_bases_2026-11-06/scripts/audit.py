import sys,json,csv,gzip,collections,hashlib,math,importlib.util
from pathlib import Path
sys.path.insert(0,'/tmp/ladefe-check/scripts')
from build_canonical import logical_table,scalar
from validate_demo import display_value
from tableauhyperapi import HyperProcess,Connection,Telemetry
R=Path('/tmp/ladefe-check'); O=Path('/tmp/ladefe-validation'); csv.field_size_limit(10000000)
def load(f):
 with gzip.open(f,'rt',encoding='utf-8-sig') as h:return list(csv.DictReader(h))
canon={}
for f in (R/'data/canonical').glob('*.csv.gz'):
 rows=load(f);canon[f.name.split('.')[0]]=rows
schema=json.loads((R/'data/canonical/schema.json').read_text()); canonical_sets={}
for name,cols in schema.items():
 key={'Grupos Indicadores':'grupos_indicadores'}.get(name,name.lower())
 canonical_sets[name]={tuple(row.get(c,'') for c in cols) for row in canon[key]}
def st(v):
 v=scalar(v)
 if v is None:return ''
 if isinstance(v,bool):return str(v)
 return str(v)
# CSV writer stores bool as True/False; actual CSV uses booleans read from strings in Hyper.
summary=[]; tables=collections.defaultdict(set); mismatches=[]; raw_demo_mismatch=[]; map_mismatch=[]; projections=[]; formula_examples=[]; alltypes=collections.Counter(); source_rows_total=0
cat=json.loads((R/'demo/catalog.json').read_text())['dashboards']; catalog={x['workbook']:x for x in cat}
rowmap={'indicatorId':'INDICADOR_ID','groupId':'GRUPO_INDICADOR_ID','type':'TIPO_DE_DATO','sectionId':'SECCION_ID','sectionName':'SECCION_NOMBRE','sourceDataId':'ID_DATO_SM','systemData':'DATO_DE_SISTEMA','year':'ANIO','month':'MES','geoCode':'UNIDAD_GEOGRAFICA_CODIGO','geoName':'UNIDAD_GEOGRAFICA_NOMBRE','subGeo':'SUB_UNIDAD_GEOGRAFICA','opening':'APERTURA_DESCRIPCION','level1':'APERTURA_NIVEL_1','mode1':'MODALIDAD_APERTURA_NIVEL_1','level2':'APERTURA_NIVEL_2','mode2':'MODALIDAD_APERTURA_NIVEL_2','rawValue':'VALOR','aux':'VALOR_AUXILIAR'}
with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,parameters={"use_tcp_port":"auto"}) as hp:
 for w,item in catalog.items():
  paths=list((O/'unpacked'/w).glob('*.hyper'))
  if not paths:summary.append({'workbook':w,'error':'no Hyper'});continue
  source={}; count=0
  for p in paths:
   with Connection(hp.endpoint,str(p)) as cn:
    for sn in cn.catalog.get_schema_names():
     for t in cn.catalog.get_table_names(sn):
      name=logical_table(str(t));cols=[str(c.name).strip('"') for c in cn.catalog.get_table_definition(t).columns];rows=cn.execute_list_query(f'SELECT * FROM {t}');count+=len(rows)
      source[name]=[dict(zip(cols,[scalar(v) for v in row])) for row in rows]
      s={tuple(st(v) for v in row) for row in rows};tables[name]|=s
      missing=s-canonical_sets.get(name,set())
      if missing:mismatches.append({'workbook':w,'table':name,'missing_distinct_rows':len(missing)})
  export=O/'source_tables';export.mkdir(exist_ok=True)
  with gzip.open(export/(w+'.json.gz'),'wt',encoding='utf-8') as handle:json.dump({k:v for k,v in source.items() if k!='shp'},handle,ensure_ascii=False,separators=(',',':'))
  demo=json.loads((R/'demo'/item['data']).read_text());did=demo['dashboard']['id']; src=[r for r in source['Datos'] if str(r['TABLERO_ID'])==did and r['INDICADOR_ID'] not in (None,0)]
  keys=[k for k in rowmap if k in demo['rows'][0] or k=='rawValue']
  def norm(v):return '' if v is None else str(v)
  ss={tuple(norm(r.get(rowmap[k])) for k in keys) for r in src};ds={tuple(norm(r.get(k,r.get('value') if k=='rawValue' else None)) for k in keys) for r in demo['rows']}
  if ss!=ds:raw_demo_mismatch.append({'workbook':w,'source_only':len(ss-ds),'demo_only':len(ds-ss)})
  inds={str(x['INDICADOR_ID']):x for x in source['Indicadores']}
  factors={'PORCENTAJE':100,'TASA_X_CIEN':100,'TASA_X_MIL':1000,'TASA_X_CIENMIL':100000,'TASA_X_MILLON':1000000,'RAZON_X_DIEZMIL':10000}
  for r in demo['rows']:
   alltypes[r['type']]+=1
   ind=inds[r['indicatorId']]; unit=ind['INDICADOR_UNIDAD_MEDIDA_CODIGO'];v=r.get('rawValue',r.get('value'));a=r['aux']
   if r['type']=='MAPA':
    expected=v if unit=='CANTIDAD' else v*factors[unit]/a if unit in factors and a else None
    if expected is None or not math.isclose(expected,display_value(r,next(i for i in demo['indicators'] if i['id']==r['indicatorId'])),rel_tol=1e-9,abs_tol=1e-9):map_mismatch.append({'workbook':w,'indicator':r['indicatorId'],'year':r['year'],'geo':r['geoName'],'unit':unit,'expected':expected,'demo':display_value(r,next(i for i in demo['indicators'] if i['id']==r['indicatorId'])),'raw':v,'aux':a})
   if r.get('year') and int(r['year'])>2026:projections.append({'workbook':w,'indicator':r['indicatorId'],'year':r['year']})
  source_rows_total+=count
  summary.append({'workbook':w,'physical_rows':count,'selected_rows':len(ss),'demo_rows':len(ds),'raw_equal':ss==ds,'table_count':len(source),'other_board_ids':sorted(set(str(r['TABLERO_ID']) for r in source['Datos'])-{did,'0'})})
  print(len(summary),w,'raw equality',ss==ds,flush=True)
extra={name:len(canonical_sets[name]-tables[name]) for name in tables}
result={'commit':'371aaae89c8a91b499d6fac20aec6ff49da376e3','workbooks':len(summary),'physical_rows':source_rows_total,'canonical_unique_current':{k:len(v) for k,v in tables.items()},'source_rows_missing_from_canonical':mismatches,'canonical_rows_not_in_current_source':extra,'raw_demo_mismatches':raw_demo_mismatch,'map_calculation_mismatches':map_mismatch,'future_year_rows':len(projections),'demo_types':dict(alltypes),'per_workbook':summary}
(O/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['per_workbook','map_calculation_mismatches']},ensure_ascii=False,indent=2));print('MAP MISMATCHES',len(map_mismatch),map_mismatch[:5])
