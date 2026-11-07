import json,sys,csv,collections,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,'/tmp/ladefe-check/scripts')
from validate_demo import display_value
R=Path('/tmp/ladefe-check');O=Path('/tmp/ladefe-validation');out=[];rules=[]
for item in json.load(open(R/'demo/catalog.json'))['dashboards']:
 w=item['workbook'];p=next((O/'unpacked'/w).glob('*.twb'));root=ET.parse(p).getroot()
 for ws in root.findall('./worksheets/worksheet'):
  refs=[x.text or '' for x in ws.findall('./table/rows')+ws.findall('./table/cols')]
  if any('VALOR' in x for x in refs):rules.append({'workbook':w,'worksheet':ws.get('name'),'shelves':refs})
 d=json.load(open(R/'demo'/item['data']));inds={i['id']:i for i in d['indicators']}
 for r in d['rows']:
  if r['type']=='MAPA':continue
  actual=display_value(r,inds[r['indicatorId']]); raw=r['value']
  if actual!=raw:out.append({'workbook':w,'indicator':r['indicatorId'],'name':inds[r['indicatorId']]['name'],'type':r['type'],'year':r['year'],'raw':raw,'demo':actual,'aux':r['aux']})
json.dump({'shelf_rules':rules,'nonmap_values_changed_by_demo':out},open(O/'semantic_rules.json','w'),ensure_ascii=False,indent=2)
print('non-map changed',len(out));print(out[:8]);print('rules',collections.Counter((x['worksheet'],tuple(x['shelves'])) for x in rules).most_common(5))
