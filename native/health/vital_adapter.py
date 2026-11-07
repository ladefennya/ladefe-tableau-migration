#!/usr/bin/env python3
"""DEIS 2024 -> native candidate aggregates. No source writes; no population denominators inferred."""
import argparse,csv,hashlib,json,sqlite3,re
from pathlib import Path
from collections import Counter
YEAR=2024
PROVINCES={'02','06','10','14','18','22','26','30','34','38','42','46','50','54','58','62','66','70','74','78','82','86','90','94'}
INFANT={'01.0 a 6 días','02.7 a 27 días','03.28 días a 11 meses','031. Menor de 1 año – Sin especificar'}
NEONATAL={'01.0 a 6 días','02.7 a 27 días'}
POST={'03.28 días a 11 meses'}
BIRTH_COLS=['PROVRES','TIPPARTO','SEXO','IMEDAD','ITIEMGEST','IMINSTRUC','IPESONAC','CUENTA']
DEATH_COLS=['PROVRES','SEXO','CAUSA','MAT','GRUPEDAD','CUENTA']
def require(condition, message):
 if not condition:raise ValueError(message)

def load(p,expected):
 with p.open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f,delimiter=';');require(reader.fieldnames==expected, ('schema changed',reader.fieldnames));rows=list(reader)
 for r in rows:
  require(r['PROVRES'] in PROVINCES|{'98','99'}, ('new geography',r['PROVRES']))
  require(r['CUENTA'].isdigit(), ('invalid count',r['CUENTA']))
  r['CUENTA']=int(r['CUENTA'])
 return rows

def aggregate(births,deaths):
 out=[];bp=Counter();dp=Counter();cohorts={n:Counter() for n in ['infant','neonatal','postneonatal','infant_unspecified_age','low_birth_weight','preterm','known_weight_births','known_gestation_births']}
 for r in births:
  p=r['PROVRES'];v=r['CUENTA'];bp[p]+=v
  if r['IPESONAC'].split('.')[0] in {'1','2','3','4','5'}:cohorts['low_birth_weight'][p]+=v
  if r['IPESONAC'].split('.')[0] != '9':cohorts['known_weight_births'][p]+=v
  if r['ITIEMGEST'].split('.')[0] != '8':cohorts['known_gestation_births'][p]+=v
  if r['ITIEMGEST'].split('.')[0] in {'1','2','3','4','5'}:cohorts['preterm'][p]+=v
 for r in deaths:
  p=r['PROVRES'];v=r['CUENTA'];dp[p]+=v
  require(re.fullmatch(r'[A-Z][0-9]{2}',r['CAUSA']), ('new cause encoding',r['CAUSA']))
  if r['GRUPEDAD'] in INFANT:cohorts['infant'][p]+=v
  if r['GRUPEDAD'] in NEONATAL:cohorts['neonatal'][p]+=v
  if r['GRUPEDAD'] in POST:cohorts['postneonatal'][p]+=v
  if r['GRUPEDAD'].startswith('031.'):cohorts['infant_unspecified_age'][p]+=v
 for p in sorted(bp.keys()|dp.keys()):
  row={'year':YEAR,'province_code':p,'map_eligible':p in PROVINCES,'births':bp[p],'deaths':dp[p]}
  row.update({k:v[p] for k,v in cohorts.items()})
  require(row['infant']==row['neonatal']+row['postneonatal']+row['infant_unspecified_age'], 'infant age partition inconsistent')
  row.update({'infant_per_1000_births':row['infant']/bp[p]*1000 if bp[p] else None,'low_birth_weight_pct_all_births':row['low_birth_weight']/bp[p]*100 if bp[p] else None,'preterm_pct_all_births':row['preterm']/bp[p]*100 if bp[p] else None,'low_birth_weight_pct_known_weight':row['low_birth_weight']/row['known_weight_births']*100 if row['known_weight_births'] else None,'preterm_pct_known_gestation':row['preterm']/row['known_gestation_births']*100 if row['known_gestation_births'] else None})
  out.append(row)
 return out

def reconcile(dbpath,agg):
 db=sqlite3.connect('file:'+str(dbpath)+'?mode=ro',uri=True);ps={r['province_code']:r for r in agg};out=[]
 mappings=[('4_2bNatalidadNacidosvivos','23','low_birth_weight'),('4_2bNatalidadNacidosvivos','24','preterm'),('4_3aMortalidadinfantilTasas','86','infant'),('4_3aMortalidadinfantilTasas','87','neonatal'),('4_3aMortalidadinfantilTasas','102','postneonatal')]
 for workbook,indicator,metric in mappings:
  rows=db.execute('SELECT geo_code,value_raw,auxiliary,observation_key FROM observations WHERE workbook=? AND indicator_id=? AND year=2024 AND view_type="MAPA"',(workbook,indicator)).fetchall();require(len(rows)==24, (workbook,indicator,len(rows)))
  for p,v,a,key in rows:
   c=ps[p];den_metric={'low_birth_weight':'known_weight_births','preterm':'known_gestation_births'}.get(metric,'births');denominator=c[den_metric];num_equal=v==c[metric];den_equal=a==denominator
   out.append({'workbook':workbook,'indicator_id':indicator,'province_code':p,'source_metric':metric,'year':2024,'source_numerator':c[metric],'tableau_numerator':v,'source_denominator':denominator,'tableau_denominator':a,'numerator_equal':num_equal,'denominator_equal':den_equal,'status':'exact_components' if num_equal and den_equal else 'difference_to_investigate','observation_key':key})
 birth=sum(x['births'] for x in agg)
 row=db.execute('SELECT source_json FROM observations WHERE workbook="4_2aNatalidad" AND indicator_id="474" AND year=2024').fetchall()
 candidates=[json.loads(x[0]) for x in row if json.loads(x[0])['APERTURA_NIVEL_1']=='Cantidad de nacimientos'];require(len(candidates)==1, 'national births comparison needs exactly one equivalent row')
 out.append({'workbook':'4_2aNatalidad','indicator_id':'474','province_code':'00','source_metric':'all_births_including_nonprovincial_codes','year':2024,'source_numerator':birth,'tableau_numerator':candidates[0]['VALOR'],'source_denominator':None,'tableau_denominator':None,'numerator_equal':birth==candidates[0]['VALOR'],'denominator_equal':True,'status':'exact_components' if birth==candidates[0]['VALOR'] else 'difference_to_investigate','observation_key':None})
 db.close();return out

def csvwrite(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 a=argparse.ArgumentParser();a.add_argument('--births',type=Path,required=True);a.add_argument('--deaths',type=Path,required=True);a.add_argument('--reference-db',type=Path);a.add_argument('--expected-births-sha256',default='ac0ac5ff8794f73c57a02b494b97401431ce901d4f5f0a5df877f372da9d85d2');a.add_argument('--expected-deaths-sha256',default='9b31baa9fb577f7c95fd5b159695a1b970fa2a2b1811f5cd5015cd03370bae5a');a.add_argument('--out',type=Path,required=True);p=a.parse_args()
 for kind in ['births','deaths']:
  expected=getattr(p,'expected_'+kind+'_sha256');actual=hashlib.sha256(getattr(p,kind).read_bytes()).hexdigest()
  require(not expected or actual==expected, (kind,'SHA-256 mismatch'))
 require(not p.out.exists() or not any(p.out.iterdir()), 'Output must be a new or empty directory; previous versions are preserved')
 p.out.mkdir(parents=True,exist_ok=True)
 b=load(p.births,BIRTH_COLS);d=load(p.deaths,DEATH_COLS);agg=aggregate(b,d);csvwrite(p.out/'province_aggregates_2024.csv',agg)
 # Age and cause are retained jointly; no disaggregation of 15–19 into 15–17 is permitted.
 death_groups=Counter()
 for r in d:death_groups[(r['PROVRES'],r['SEXO'],r['GRUPEDAD'],r['CAUSA'],r['MAT'])]+=r['CUENTA']
 detailed=[dict(year=2024,province_code=k[0],sex_code=k[1],age_group_source=k[2],cause_icd10_3=k[3],maternal_flag_source=k[4],deaths=v) for k,v in sorted(death_groups.items())];csvwrite(p.out/'death_dimensions_2024.csv',detailed)
 rec=reconcile(p.reference_db,agg) if p.reference_db else [];csvwrite(p.out/'reconciliation.csv',rec) if rec else None
 summary={'year':2024,'birth_source_rows':len(b),'death_source_rows':len(d),'births_all_codes':sum(x['births'] for x in agg),'deaths_all_codes':sum(x['deaths'] for x in agg),'infant_deaths_all_codes':sum(x['infant'] for x in agg),'province_codes':len(agg),'map_provinces':sum(x['map_eligible'] for x in agg),'nonmap_codes':['98','99'],'comparison_cases':len(rec),'exact_component_matches':sum(r['status']=='exact_components' for r in rec),'differences':sum(r['status']!='exact_components' for r in rec),'status':'candidate_not_published','sha256':{'births':hashlib.sha256(p.births.read_bytes()).hexdigest(),'deaths':hashlib.sha256(p.deaths.read_bytes()).hexdigest()}}
 (p.out/'reconciliation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(p.out/'candidate.json').write_text(json.dumps({'source':'DEIS official CSV, 2024','publication_status':'candidate_not_published','aggregates':agg},ensure_ascii=False,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
