"""Candidate EPH total urbano migration composition; aggregate public outputs only.
Python standard library. Never modifies the LADEFE source database.
"""
import argparse,collections,csv,hashlib,io,json,sqlite3,zipfile
from pathlib import Path
SOURCE_URL='https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_Tot_Urbano_3T_2025.zip'
DOC_URL='https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_tot_urbano_estructura_bases_2025.pdf'
LABELS={'same_province':'En la provincia en la que vive','other_province':'En otra provincia','foreign_country':'En otro país','unknown':'Sin información de lugar de nacimiento'}

def birth_group(code):
 return {'1':'same_province','2':'same_province','3':'other_province','4':'foreign_country','5':'foreign_country','9':'unknown'}[str(code)]

def aggregate(rows,age_policy='all',missing_policy='show_unknown'):
 if age_policy not in ('all','ages_1_17','ages_minus1_17'):raise ValueError('Unknown age policy')
 if missing_policy not in ('show_unknown','valid_responses'):raise ValueError('Unknown missing-data policy')
 counts=collections.Counter();sample=collections.Counter();selected=0
 for r in rows:
  age=int(r['CH06']);w=int(r['PONDERA'])
  if w<0:raise ValueError('Negative PONDERA')
  if age_policy=='ages_1_17' and not 1<=age<=17:continue
  if age_policy=='ages_minus1_17' and not -1<=age<=17:continue
  selected+=1;g=birth_group(r['CH15']);counts[g]+=w;sample[g]+=1
 denominator=sum(counts.values())-(counts['unknown'] if missing_policy=='valid_responses' else 0)
 if denominator<=0:raise ValueError('Empty denominator')
 groups=list(LABELS) if missing_policy=='show_unknown' else list(LABELS)[:3]
 result=[{'category':g,'label':LABELS[g],'numerator':counts[g],'denominator':denominator,'value':100*counts[g]/denominator,'sample_n':sample[g],'missing_policy':missing_policy,'age_policy':age_policy,'year':2025,'period':'T3','geo_code':'00','unit':'PORCENTAJE','status':'candidate_unapproved'} for g in groups]
 if abs(sum(r['value'] for r in result)-100)>=1e-9:raise ValueError('Category shares do not sum to 100')
 return result,{'sample_total':selected,'weighted_total':sum(counts.values()),'unknown_weight':counts['unknown'],'unknown_n':sample['unknown']}

def run(input_path,db_path,out):
 if out.exists() and (not out.is_dir() or any(out.iterdir())):raise ValueError('Output must be new or empty; existing results are immutable')
 out.mkdir(parents=True,exist_ok=True);b=input_path.read_bytes();z=zipfile.ZipFile(io.BytesIO(b));name='personas_tot.urb_3T_2025.txt';rows=list(csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig')),delimiter=';'))
 required={'CODUSU','NRO_HOGAR','COMPONENTE','AGLOMERADO','ANO4','TRIMESTRE','PROVINCIA','CH06','CH15','PONDERA'}
 if not rows:raise ValueError('Empty source')
 if not required<=rows[0].keys():raise ValueError('Missing source columns')
 if {r['ANO4'] for r in rows}!={'2025'} or {r['TRIMESTRE'] for r in rows}!={'3'}:raise ValueError('Source is not 2025/T3')
 keys=[tuple(r[k] for k in ['CODUSU','AGLOMERADO','NRO_HOGAR','COMPONENTE']) for r in rows]
 if len(keys)!=len(set(keys)):raise ValueError('Duplicate person keys')
 output=[];diagnostics={}
 for age in ['all','ages_minus1_17','ages_1_17']:
  for missing in ['show_unknown','valid_responses']:
   rs,d=aggregate(rows,age,missing);output+=rs;diagnostics[age+'/'+missing]=d
 D=sqlite3.connect('file:'+str(db_path)+'?mode=ro',uri=True);comparison=[]
 for raw, in D.execute("SELECT source_json FROM observations WHERE workbook='8_3bNNyAmigrantes_Losmigrantesenlasreasurbanas' AND indicator_id='1048' AND year=2025"):
  r=json.loads(raw);age='all' if r['APERTURA_NIVEL_1']=='Población urbana' else 'ages_minus1_17'
  for candidate in output:
   if candidate['age_policy']==age and candidate['label']==r['MODALIDAD_APERTURA_NIVEL_1']:
    comparison.append({'population':r['APERTURA_NIVEL_1'],'category':candidate['category'],'missing_policy':candidate['missing_policy'],'age_policy':age,'tableau':r['VALOR'],'recomputed':candidate['value'],'difference_pp':candidate['value']-r['VALOR'],'matches_one_decimal':round(candidate['value'],1)==r['VALOR']})
 D.close()
 (out/'candidate_migration_national.json').write_text(json.dumps(output,ensure_ascii=False,indent=2))
 (out/'reconciliation.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2))
 (out/'diagnostics.json').write_text(json.dumps({'source_url':SOURCE_URL,'codebook_url':DOC_URL,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'sample_rows':len(rows),'years':[2025],'periods':['T3'],'duplicate_person_keys':0,'province_codes':sorted({r['PROVINCIA'] for r in rows}),'age_minus_one_n':sum(r['CH06']=='-1' for r in rows),'age_policy_note':'ages_minus1_17 is an explicit sensitivity case; obtain confirmation of age -1 before approving child universe','groups':diagnostics,'release_status':'blocked_pending_semantic_review'},ensure_ascii=False,indent=2))
 with (out/'reconciliation.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
 print('PASS: source rows',len(rows),'aggregate outputs',len(output),'comparison records',len(comparison))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--database',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.input,a.database,a.out)
