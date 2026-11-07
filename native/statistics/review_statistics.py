"""Read-only statistical contract review. Standard library only."""
import argparse,collections,json,sqlite3,xml.etree.ElementTree as ET
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--database',type=Path,required=True);P.add_argument('--repo',type=Path,required=True);P.add_argument('--twb-root',type=Path);P.add_argument('--out',type=Path,required=True);a=P.parse_args();a.out.mkdir(parents=True,exist_ok=True)
d=sqlite3.connect('file:'+str(a.database)+'?mode=ro',uri=True);d.row_factory=sqlite3.Row
allrows=[dict(r) for r in d.execute('SELECT * FROM native_data')]
e={'counts':{'observations':len(allrows),'workbooks':len({r['workbook'] for r in allrows}),'unit_counts':dict(collections.Counter(r['unit'] for r in allrows)),'view_counts':dict(collections.Counter(r['view_type'] for r in allrows))},'future_raw_year':[r for r in allrows if r['year'] and r['year']>2026], 'temporal_case_records':[], 'distribution_candidates':[], 'duplicates_source_ids':[]}
for r in allrows:
 if (r['workbook'],r['indicator_id']) in [('4_1Coberturadesalud','789'),('3_2eEstablecimientosEntregadealimentos','465')]:
  source=json.loads(r['source_json']);e['temporal_case_records'].append({'workbook':r['workbook'],'indicator_id':r['indicator_id'],'observation_key':r['observation_key'],'source_id':source['ID_DATO_SM'],'raw_year':r['year'],'age_or_level':source['MODALIDAD_APERTURA_NIVEL_1'],'second_dimension':source['APERTURA_NIVEL_2'],'second_modality':source['MODALIDAD_APERTURA_NIVEL_2'],'raw_value':r['value_raw'],'view_type':r['view_type']})
G=collections.defaultdict(list)
for r in allrows:
 if r['view_type']=='DISTRIBUCION' and r['unit']=='PORCENTAJE':
  di=json.loads(r['dimensions_json']);di={k:v for k,v in di.items() if k not in ['MODALIDAD_APERTURA_NIVEL_1','MODALIDAD_APERTURA_NIVEL_2']};G[(r['workbook'],r['indicator_id'],json.dumps(di,sort_keys=True))].append(r)
for (w,i,di),rs in G.items():
 if len(rs)<2:continue
 total=sum(r['value_display'] for r in rs);tol=.05*len(rs) # Candidate only, assuming one decimal and exhaustive nonoverlapping categories.
 if abs(total-100)>tol+1e-8:e['distribution_candidates'].append({'workbook':w,'indicator_id':i,'dimensions':json.loads(di),'values':[r['value_display'] for r in rs],'sum':total,'one_decimal_max_rounding_error_pp':tol,'state':'pending_thematic_partition_confirmation'})
e['counts']['distribution_candidate_groups_tested']=sum(len(rs)>1 for rs in G.values())
e['counts']['metadata_id_variants']=d.execute('SELECT COUNT(*) FROM (SELECT indicator_id,COUNT(DISTINCT metadata_json) n FROM indicators GROUP BY indicator_id HAVING n>1)').fetchone()[0]
e['duplicates_source_ids']=[dict(r) for r in d.execute("SELECT workbook,json_extract(source_json,'$.ID_DATO_SM') source_id,COUNT(*) n FROM observations GROUP BY 1,2 HAVING n>1")]
e['counts']['nonmap_with_auxiliary']=sum(r['view_type']!='MAPA' and r['auxiliary'] is not None for r in allrows)
e['counts']['map_invalid_denominator']=sum(r['view_type']=='MAPA' and r['calculation']=='ratio_mapa' and (r['auxiliary'] is None or r['auxiliary']<=0) for r in allrows)
shelves=[]
if a.twb_root:
 for p in sorted(a.twb_root.glob('*/*.twb')):
  root=ET.parse(p).getroot()
  for ws in root.findall('./worksheets/worksheet'):
   refs=[x.text or '' for x in ws.findall('./table/rows')+ws.findall('./table/cols')]
   if any('avg:VALOR' in x for x in refs):shelves.append({'workbook':p.parent.name,'worksheet':ws.get('name'),'references':refs})
e['tableau_avg_shelves']=shelves
(a.out/'evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2))
print(json.dumps({'counts':e['counts'],'future_rows':len(e['future_raw_year']),'temporal_cases':len(e['temporal_case_records']),'distribution_alerts':len(e['distribution_candidates']),'avg_workbooks':len({r['workbook'] for r in shelves}),'avg_shelves':len(shelves)},ensure_ascii=False,indent=2))
