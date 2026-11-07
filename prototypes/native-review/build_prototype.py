"""Build a self-contained candidate UI from a frozen display payload. No database or network."""
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser(description=__doc__)
for name in ['data','template','contract','out']:p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args()
data_bytes=a.data.read_bytes();P=json.loads(data_bytes)
if not isinstance(P,dict) or not isinstance(P.get('catalog'),dict) or not P['catalog']:
 raise SystemExit('Invalid frozen display payload: catalog required')
for k,d in P['catalog'].items():
 for field in ['title','rows','release','snapshot','sourceURL','periods','domain','universes','geos']:
  if field not in d:raise SystemExit(f'Invalid dataset {k}: missing {field}')
template_bytes=a.template.read_bytes();contract_bytes=a.contract.read_bytes();t=template_bytes.decode('utf-8');contract=contract_bytes.decode('utf-8')
if t.count('__DATA__')!=1 or t.count('__CONTRACT__')!=1:raise SystemExit('Template placeholders must occur exactly once')
h=t.replace('__DATA__',json.dumps(P,ensure_ascii=False).replace('</','<\\/')).replace('__CONTRACT__',contract)
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(h,encoding='utf-8')
manifest={'entrypoint':a.out.name,'external_dependencies':[],'network_requests_required':False,'resources':[{'path':a.out.name,'sha256':hashlib.sha256(h.encode()).hexdigest(),'role':'self-contained candidate interface; all CSS JS data embedded'}],'build_inputs_sha256':{'frozen_payload':hashlib.sha256(data_bytes).hexdigest(),'template':hashlib.sha256(template_bytes).hexdigest(),'query_contract':hashlib.sha256(contract_bytes).hexdigest()},'sources':[{'dataset':k,'release':v['release'],'snapshot':v['snapshot'],'url':v['sourceURL'],'rows':len(v['rows'])} for k,v in P['catalog'].items()],'approval_status':'prototype_not_approved','map_gate':P['mapGate']}
a.out.with_name('resources_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(a.out);print('bytes',len(h.encode()))
