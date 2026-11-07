"""Produce reproducible evidence for cycle labels and the 8.1 vs 8.047 case."""
import argparse,hashlib,io,json,sqlite3,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import openpyxl
from education_adapter import WB,extract,reconcile,rounded

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-zip',type=Path,required=True);p.add_argument('--reference-db',type=Path,required=True);p.add_argument('--tableau-twb',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():raise SystemExit('Evidence destination already exists; preserve previous versions')
 z=zipfile.ZipFile(a.source_zip);member=next(n for n in z.namelist() if n.endswith('.xlsx') and 'división político-territorial' in n);w=openpyxl.load_workbook(io.BytesIO(z.read(member)),data_only=True);cell=w['2023-2024']['K12'];rs,meta=extract(a.source_zip);comparison=reconcile(rs,a.reference_db)
 twb=ET.parse(a.tableau_twb).getroot();format_evidence=[dict(e.attrib) for e in twb.iter() if e.tag=='column' and e.attrib.get('name')=='[VALOR]' and e.attrib.get('default-format')];format_evidence=[dict(t) for t in {tuple(sorted(x.items())) for x in format_evidence}]
 with sqlite3.connect('file:'+str(a.reference_db.resolve())+'?mode=ro',uri=True) as d:
  case=d.execute('SELECT source_json,observation_key FROM observations WHERE workbook=? AND indicator_id=? AND year=2023',(WB,'384')).fetchall();case=[{'source_json':json.loads(x[0]),'observation_key':x[1]} for x in case if 'secundario' in str(json.loads(x[0])['MODALIDAD_APERTURA_NIVEL_1'])];count=d.execute('SELECT COUNT(*) FROM observations WHERE workbook=? AND indicator_id IN (?,?,?,?,?)',(WB,'380','381','382','383','384')).fetchone()[0]
 evidence={'source_sha256':hashlib.sha256(a.source_zip.read_bytes()).hexdigest(),'source_member_sha256':hashlib.sha256(z.read(member)).hexdigest(),'reference_sha256':hashlib.sha256(a.reference_db.read_bytes()).hexdigest(),'twb_sha256':hashlib.sha256(a.tableau_twb.read_bytes()).hexdigest(),'rounding_case':{'cell':'K12','sheet':'2023-2024','source_raw':cell.value,'source_number_format':cell.number_format,'official_display_2dp':str(rounded(cell.value,2)),'direct_to_1dp':str(rounded(cell.value,1)),'display_then_1dp':str(rounded(rounded(cell.value,2),1)),'reference':case,'worksheet_preparation_note':[r[0].value for r in w['2023-2024'] if str(r[0].value).startswith('Realización')],'conclusion':'compatible with double rounding of the official displayed value, not proof of the historical ETL route; no automatic replacement'},'tableau_format_evidence':format_evidence,'temporal_conflicts':[r for r in comparison if r['period_label_conflict']],'scope':{'all_reference_dropout_rows':count,'reconciled':len(comparison),'coverage_complete_for_five_declared_ids':count==len(comparison),'other_five_workbook_indicators':'promotion; not in dropout source and deliberately excluded'}}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print(json.dumps({'reference_dropout_rows':count,'temporal_conflicts':len(evidence['temporal_conflicts']),'direct_to_1dp':str(rounded(cell.value,1)),'display_then_1dp':str(rounded(rounded(cell.value,2),1))},indent=2))
if __name__=='__main__':main()
