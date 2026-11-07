import gzip,json,collections,sys
from pathlib import Path
O=Path('/tmp/ladefe-validation');R=Path('/tmp/ladefe-check');cat=json.load(open(R/'demo/catalog.json'))['dashboards'];report=[]
for item in cat:
 p=O/'source_tables'/(item['workbook']+'.json.gz')
 if not p.exists():continue
 d=json.load(gzip.open(p,'rt'));did=json.load(open(R/'demo'/item['data']))['dashboard']['id'];rows=[r for r in d['Datos'] if str(r['TABLERO_ID'])==did and r['INDICADOR_ID'] not in (0,None)];ids={str(x['INDICADOR_ID']):x for x in d['Indicadores']};gs={str(x['GRUPO_INDICADOR_ID']):x for x in d['Grupos Indicadores']};keys=[k for k in rows[0] if k not in ['ID_DATO_SM','VALOR','VALOR_AUXILIAR','DATO_DE_SISTEMA']] if rows else []
 c=collections.Counter(tuple(str(r[k]) for k in keys) for r in rows); conflicts=sum(v>1 for v in c.values())
 used={str(r['INDICADOR_ID']) for r in rows};units=collections.Counter(ids[i]['INDICADOR_UNIDAD_MEDIDA_CODIGO'] for i in used if i in ids)
 report.append({'workbook':item['workbook'],'source_rows':len(rows),'indicators':len(used),'orphan_indicators':sum(str(r['INDICADOR_ID']) not in ids for r in rows),'orphan_groups':sum(str(r['GRUPO_INDICADOR_ID']) not in gs for r in rows),'dimension_keys_with_multiple_rows':conflicts,'null_values':sum(r['VALOR'] is None for r in rows),'units':dict(units),'years':sorted({r['ANIO'] for r in rows if r['ANIO'] is not None}),'missing_formula':sum(not str(ids[i].get('INDICADOR_FORMULA') or '').strip() for i in used if i in ids),'missing_methodology':sum(not str(ids[i].get('INDICADOR_DESC_METODOLOGICA') or '').strip() for i in used if i in ids),'within_source_indicator_id_duplicates':len(d['Indicadores'])-len(ids)})
json.dump(report,open(O/'quality.json','w'),ensure_ascii=False,indent=2)
print('boards',len(report),'source_rows',sum(x['source_rows'] for x in report));print({k:sum(x[k] for x in report) for k in ['orphan_indicators','orphan_groups','dimension_keys_with_multiple_rows','null_values','missing_formula','missing_methodology','within_source_indicator_id_duplicates']})
