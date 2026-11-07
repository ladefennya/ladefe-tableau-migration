import argparse,sqlite3,json,csv,collections,unicodedata,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--database',type=Path,required=True);p.add_argument('--geojson',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
O=a.out;O.mkdir(parents=True,exist_ok=True)
D=sqlite3.connect(a.database.resolve().as_uri()+'?mode=ro',uri=True);D.row_factory=sqlite3.Row
norm=lambda x:''.join(c for c in unicodedata.normalize('NFD',str(x or '').upper()) if c.isalpha())
geo=json.loads(a.geojson.read_text());codes={'02':'Ciudad Autónoma de Buenos Aires','06':'Buenos Aires','10':'Catamarca','14':'Córdoba','18':'Corrientes','22':'Chaco','26':'Chubut','30':'Entre Ríos','34':'Formosa','38':'Jujuy','42':'La Pampa','46':'La Rioja','50':'Mendoza','54':'Misiones','58':'Neuquén','62':'Río Negro','66':'Salta','70':'San Juan','74':'San Luis','78':'Santa Cruz','82':'Santa Fe','86':'Santiago del Estero','90':'Tucumán','94':'Tierra del Fuego'}
lookup={norm(v):k for k,v in codes.items()};lookup.update({'CABA':'02','CAPITALFEDERAL':'02',norm('Tierra del Fuego, Antártida e Islas del Atlántico Sur'):'94'})
for k,v in codes.items():lookup[norm('Provincia de '+v)]=k
allrows=[dict(r) for r in D.execute('SELECT * FROM native_data')];by=collections.defaultdict(list);slices=collections.defaultdict(list);candidates=[]
for r in allrows:
 by[(r['workbook'],r['indicator_id'])].append(r)
 if r['view_type']=='MAPA':
  raw=json.loads(r['source_json']);dims={k:v for k,v in raw.items() if k not in ['UNIDAD_GEOGRAFICA_CODIGO','UNIDAD_GEOGRAFICA_NOMBRE','ID_DATO_SM','VALOR','VALOR_AUXILIAR','DATO_DE_SISTEMA']};slices[(r['workbook'],r['indicator_id'],json.dumps(dims,sort_keys=True,ensure_ascii=False))].append(r)
indicator_rows=[]
for (w,i),rs in by.items():
 maps=[r for r in rs if r['view_type']=='MAPA'];latent=[]
 for field in ['MODALIDAD_APERTURA_NIVEL_1','MODALIDAD_APERTURA_NIVEL_2','SUB_UNIDAD_GEOGRAFICA']:
  matched=[(r,lookup.get(norm(json.loads(r['source_json']).get(field)))) for r in rs if r['view_type']!='MAPA'];matched=[x for x in matched if x[1]]
  unique={x[1] for x in matched}
  if len(unique)>=2:
   latent.append((field,len(matched),len(unique)))
   for r,code in matched:candidates.append({'workbook':w,'indicator_id':i,'name':r['indicator_name'],'view_type':r['view_type'],'field':field,'candidate_province_code':code,'source_observation_key':r['observation_key'],'value':r['value_raw'],'status':'correspondencia textual exacta; requiere curación de unidad, población y período'})
 nden=sum(r['auxiliary'] is None or r['auxiliary']==0 for r in maps if r['unit']!='CANTIDAD');vals=[r['value_display'] for r in maps if r['value_display'] is not None]
 indicator_rows.append({'workbook':w,'indicator_id':i,'name':rs[0]['indicator_name'],'unit':rs[0]['unit'],'rows':len(rs),'map_rows':len(maps),'map_provinces_union':len({r['geo_code'] for r in maps}),'latent_province_dimensions':json.dumps(latent,ensure_ascii=False),'map_missing_denominator':nden,'negative_map_values':sum(v<0 for v in vals),'map_eligibility':'geometría y valores disponibles; comparabilidad temática pendiente' if maps else 'candidato desde apertura; requiere transformación aprobada' if latent else 'sin dimensión provincial cartografiable identificada','recommended_primary':'símbolos proporcionales/ranking para cantidades' if maps and rs[0]['unit']=='CANTIDAD' else 'coropleta de tasa/cobertura solo con denominador compatible; ranking siempre' if maps else 'ranking/tabla y mapa opcional tras curación' if latent else 'serie/distribución/tabla; no forzar mapa'})
coverage=[]
for (w,i,k),rs in slices.items():
 seen={r['geo_code'] for r in rs};coverage.append({'workbook':w,'indicator_id':i,'dimensions':k,'rows':len(rs),'jurisdictions':len(seen),'missing_province_codes':','.join(sorted(set(codes)-seen)),'duplicate_codes':len(rs)-len(seen),'null_display_values':sum(r['value_display'] is None for r in rs)})
boards=[]
for b in D.execute('SELECT workbook,metadata_json FROM boards'):
 rs=[r for r in indicator_rows if r['workbook']==b['workbook']];ms=[r for r in coverage if r['workbook']==b['workbook']];boards.append({'workbook':b['workbook'],'name':json.loads(b['metadata_json'])['TABLERO_NOMBRE'],'indicators':len(rs),'map_indicators':sum(r['map_rows']>0 for r in rs),'latent_only_indicators':sum(bool(json.loads(r['latent_province_dimensions'])) and not r['map_rows'] for r in rs),'map_slices':len(ms),'complete_24_slices':sum(x['jurisdictions']==24 for x in ms),'incomplete_slices':sum(x['jurisdictions']<24 for x in ms),'max_province_codes':max([r['map_provinces_union'] for r in rs],default=0),'eligibility':'mapa provincial existente' if any(r['map_rows'] for r in rs) else 'potencial a curar en aperturas' if any(json.loads(r['latent_province_dimensions']) for r in rs) else 'sin mapa provincial justificable con datos actuales'})
def csvout(name,rs):
 if rs:
  with (O/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
csvout('matriz_71_cartografia.csv',boards);csvout('matriz_indicadores_cartografia.csv',indicator_rows);csvout('cobertura_cortes_mapa.csv',coverage);csvout('geografia_en_aperturas_candidatos.csv',candidates)
# Source GeoJSON is geographic lon/lat from the workflow EPSG:4326; numeric extent and ring checks only, no visual approval.
def rings(g):return g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p]
features=[]
for f in geo['features']:
 rr=rings(f['geometry']);points=[p for r in rr for p in r];name=f['properties']['nam'];features.append({'name':name,'candidate_code':lookup.get(norm(name)),'rings':len(rr),'points':len(points),'bbox':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],'unclosed_rings':sum(r[0]!=r[-1] for r in rr),'rings_under_4_points':sum(len(r)<4 for r in rr),'nonfinite_coordinates':sum(not all(math.isfinite(v) for v in p) for p in points)})
summary={'boards':len(boards),'indicator_links':len(indicator_rows),'map_boards':sum(x['map_indicators']>0 for x in boards),'latent_only_boards':sum(x['map_indicators']==0 and x['latent_only_indicators']>0 for x in boards),'map_indicator_links':sum(x['map_rows']>0 for x in indicator_rows),'latent_only_indicator_links':sum(bool(json.loads(x['latent_province_dimensions'])) and not x['map_rows'] for x in indicator_rows),'map_rows':sum(x['map_rows'] for x in indicator_rows),'map_slices':len(coverage),'complete_slices':sum(x['jurisdictions']==24 for x in coverage),'incomplete_slices':sum(x['jurisdictions']<24 for x in coverage),'nonmap_candidate_rows':len(candidates),'geo_feature_count':len(features),'geo_numeric_checks':features,'rules':'No certification of topology, area accuracy, visual appearance or conceptual comparability.'}
(O/'resumen_cartografia.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print({k:v for k,v in summary.items() if k!='geo_numeric_checks'})
