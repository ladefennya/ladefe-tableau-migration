import sqlite3,json,gzip,hashlib,sys,math
from pathlib import Path
O=Path(sys.argv[1]);S=Path(sys.argv[2]);d=sqlite3.connect(O/'base_maestra.sqlite');manifest=json.load(open(O/'manifest.json'));n=0
for name,digest in manifest['source_files'].items():
 p=S/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 source=json.load(gzip.open(p,'rt'));w=name[:-8]
 for table,rows in source.items():
  original={json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')) for r in rows}
  stored={r[0] for r in d.execute('SELECT p.payload_json FROM source_records s JOIN source_payloads p USING(row_hash) WHERE s.workbook=? AND s.table_name=?',(w,table))}
  assert original==stored,(w,table);n+=len(original)
checked=0
for r,v,aux,display,mode,unit in d.execute('SELECT source_json,value_raw,auxiliary,value_display,calculation,unit FROM native_data'):
 r=json.loads(r);assert v==r['VALOR'] and aux==r['VALOR_AUXILIAR']
 if mode=='ratio_mapa':
  factor={'PORCENTAJE':100,'TASA_X_CIEN':100,'TASA_X_MIL':1000,'TASA_X_CIENMIL':100000,'TASA_X_MILLON':1000000,'RAZON_X_DIEZMIL':10000}[unit];assert math.isclose(display,v/aux*factor,rel_tol=1e-12)
 else:assert display==v
 checked+=1
assert d.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert d.execute('PRAGMA foreign_key_check').fetchall()==[]
result={'source_files_sha256':71,'source_records_roundtrip':n,'observations_verified':checked,'sqlite_integrity':'ok','foreign_keys':'ok','result':'PASS'};(O/'verification.json').write_text(json.dumps(result,indent=2));print(result)
