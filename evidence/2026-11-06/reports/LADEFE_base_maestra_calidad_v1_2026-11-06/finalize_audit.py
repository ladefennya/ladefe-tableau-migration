import sqlite3,json,csv,collections,hashlib,sys
from pathlib import Path
O=Path(sys.argv[1]);d=sqlite3.connect(O/'base_maestra.sqlite');d.row_factory=sqlite3.Row
usable=lambda x:any(c.isalnum() for c in str(x or '')) and ' '.join(str(x or '').split()).lower() not in ('sin información','sin informacion','s/d','no disponible','sin datos')
d.execute("DELETE FROM findings WHERE rule='metadata_incompleta'")
rows=list(csv.DictReader(open(O/'diccionario_indicadores.csv',encoding='utf-8-sig')))
for r in rows:
 missing=[]
 for col,field in [('definition','INDICADOR_DEFINICION'),('methodology','INDICADOR_DESC_METODOLOGICA'),('formula','INDICADOR_FORMULA'),('unit','INDICADOR_UNIDAD_MEDIDA_CODIGO')]:
  if not usable(r[col]):
   missing.append(field);d.execute('INSERT INTO findings(rule,severity,workbook,indicator_id,evidence_json) VALUES(?,?,?,?,?)',('metadata_incompleta','advertencia',r['workbook'],r['indicator_id'],json.dumps({'field':field},ensure_ascii=False)))
 r['missing_fields']=' | '.join(missing)
def write(name,rows):
 with open(O/name,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('diccionario_indicadores.csv',rows);write('hallazgos.csv',[dict(r) for r in d.execute('SELECT rule,severity,workbook,indicator_id,observation_key,evidence_json FROM findings ORDER BY id')]);s=json.load(open(O/'resumen.json'));s['findings_by_rule']=dict(d.execute('SELECT rule,COUNT(*) FROM findings GROUP BY rule'));s['findings_by_severity']=dict(d.execute('SELECT severity,COUNT(*) FROM findings GROUP BY severity'));s['metadata_missing_fields']=dict(d.execute("SELECT json_extract(evidence_json,'$.field'),COUNT(*) FROM findings WHERE rule='metadata_incompleta' GROUP BY 1"));d.commit();assert d.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not d.execute('PRAGMA foreign_key_check').fetchall();s['sqlite_integrity']='ok';s['sqlite_foreign_keys']='ok';(O/'resumen.json').write_text(json.dumps(s,ensure_ascii=False,indent=2));print(json.dumps(s,indent=2));d.close()
