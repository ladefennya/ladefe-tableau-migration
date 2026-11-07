import argparse,sqlite3,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from publication_gate import temporal_proposal
a=argparse.ArgumentParser();a.add_argument('--database',type=Path,required=True);a.add_argument('--twb-root',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
O=args.out;O.mkdir(parents=True,exist_ok=True);db=args.database;D=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
records=[]
for w in ['4_1Coberturadesalud','3_2eEstablecimientosEntregadealimentos']:
 rows=D.execute('SELECT observation_key,source_json FROM observations WHERE workbook=? AND indicator_id=? ORDER BY year',(w,'789' if w.startswith('4_1') else '465')).fetchall()
 p=next((args.twb_root/w).glob('*.twb'));root=ET.parse(p).getroot();xml_sha=hashlib.sha256(p.read_bytes()).hexdigest();worksheets=[]
 for ws in root.findall('./worksheets/worksheet'):
  if ws.get('name') not in ('Cruces Relevantes - Aperturas y Grupos - Barras','Cruces Relevantes - Aperturas y Grupos - Tabla'):continue
  shelves={x.tag:x.text for x in ws.findall('./table/rows')+ws.findall('./table/cols')};year_filters=[ET.tostring(x,encoding='unicode') for x in ws.findall('.//filter') if 'ANIO' in x.get('column','')];worksheets.append({'name':ws.get('name'),'shelves':shelves,'year_filters':year_filters})
 for key,src in rows:
  r=json.loads(src);proposal=temporal_proposal(r,w);proposal.update(workbook=w,observation_key=key,decision={'state':'pending','approver':None,'approved_at':None,'evidence':{'source_sqlite':str(db),'source_id':r['ID_DATO_SM'],'xml_sha256':xml_sha,'xml_file':p.name,'worksheets':worksheets},'scope':{'snapshot':'2026-11-06','workbook':w,'indicator_id':str(r['INDICADOR_ID']),'observation_key':key}});records.append(proposal)
(O/'temporal_decisions.json').write_text(json.dumps({'schema_version':'0.2.0','raw_data_modified':False,'records':records},ensure_ascii=False,indent=2));print('Records',len(records),'proposed census periods',sum(r['reference_period_candidate'] is not None for r in records))
