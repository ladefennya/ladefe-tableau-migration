"""Static evidence only: does not audit rendered design or accessibility conformance."""
import argparse,collections,json,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--database',type=Path,required=True);p.add_argument('--demo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
d=sqlite3.connect(a.database.resolve().as_uri()+'?mode=ro',uri=True)
c=json.loads((a.demo/'catalog.json').read_text())['dashboards'];app=(a.demo/'app.js').read_text();html=(a.demo/'index.html').read_text()
result={
 'scope':'static source + SQLite; no browser/user testing',
 'topics':dict(collections.Counter(x['topic'] for x in c)),
 'types':[dict(zip(['view_type','rows','workbooks'],r)) for r in d.execute('select view_type,count(*),count(distinct workbook) from observations group by view_type')],
 'observations':d.execute('select count(*) from observations').fetchone()[0],
 'selected_controls_present':{i:('id="'+i+'"') in html for i in ['topic','board','indicator','type','year','territory','opening','period','search']},
 'static_flags':{'table_slice_250':'rows.slice(0,250)' in app,'series_slice_6':'valid.slice(0,6)' in app,'history_replaceState':'history.replaceState' in app,'popstate_handler':'popstate' in app,'regex_national':'/total|argentina|nacional|país/i' in app,'visible_label_lastDataLoad':'data.dashboard.lastDataLoad' in app},
 'territorial_aperture_candidates':d.execute("select indicator_id,indicator_name,count(*) from native_data where workbook='2_2bAUH' and indicator_id in ('217','423') group by indicator_id").fetchall()
}
a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
