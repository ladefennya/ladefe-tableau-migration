"""Pinned EPH total urbano migration diagnostics, never an automatic replacement.
Source domains are fixed to the two downloaded editions. No network or source writes.
"""
import argparse,collections,csv,hashlib,io,json,re,sqlite3,zipfile
from decimal import Decimal
from pathlib import Path
LABELS={'same_province':'En la provincia en la que vive','other_province':'En otra provincia','foreign_country':'En otro país','unknown':'Sin información de lugar de nacimiento'}
PROVINCES={'02','06','10','14','18','22','26','30','34','38','42','46','50','54','58','62','66','70','74','78','82','86','90','94'}
REQUIRED={'CODUSU','NRO_HOGAR','COMPONENTE','AGLOMERADO','ANO4','TRIMESTRE','PROVINCIA','CH06','CH15','PONDERA'}
DOC_URL='https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_tot_urbano_estructura_bases_2025.pdf'
REGISTRY_PATH=Path(__file__).with_name('source_registry.json')
def require(value,message):
 if not value:raise ValueError(message)
def integer(value,label):
 require(isinstance(value,str) and re.fullmatch(r'-?\d+',value) is not None,'Invalid integer: '+label)
 return int(value)
def birth_group(code):
 mapping={'1':'same_province','2':'same_province','3':'other_province','4':'foreign_country','5':'foreign_country','9':'unknown'}
 require(str(code) in mapping,'Unknown CH15 birth category')
 return mapping[str(code)]
def matches_decimal(numerator,denominator,reference,decimals=1):
 require(denominator>0,'Empty denominator')
 value=Decimal(numerator)*100/Decimal(denominator);target=Decimal(str(reference));half=Decimal(5).scaleb(-decimals-1)
 return abs(value-target)<=half

def validate_rows(rows,year,profile=None):
 require(bool(rows),'Empty source');require(REQUIRED<=rows[0].keys(),'Missing required fields')
 keys=set();weights=0
 for r in rows:
  require(None not in r and all(r.get(c) is not None for c in REQUIRED),'Malformed or short CSV record')
  require(integer(r['ANO4'],'ANO4')==year and integer(r['TRIMESTRE'],'TRIMESTRE')==3,'Unexpected year/quarter')
  require(r['CODUSU']==r['CODUSU'].strip() and bool(r['CODUSU']),'Empty/noncanonical household key')
  for c in ('NRO_HOGAR','COMPONENTE','AGLOMERADO'):require(integer(r[c],c)>0,'Nonpositive identity dimension '+c)
  require(r['PROVINCIA'].zfill(2) in PROVINCES,'Unknown province')
  age=integer(r['CH06'],'CH06');require(age==-1 or 0<=age<=120 or age==999,'Unexpected age code')
  weight=integer(r['PONDERA'],'PONDERA');require(weight>0,'Nonpositive weight');weights+=weight;birth_group(r['CH15'])
  key=tuple(r[c] for c in ('CODUSU','AGLOMERADO','NRO_HOGAR','COMPONENTE'))
  require(key not in keys,'Duplicate person key');keys.add(key)
 if profile:
  require(len(rows)==profile['sample_rows'],'Pinned source row count mismatch')
  require(weights==profile['weighted_total'],'Pinned source weight total mismatch')
 return {'sample_rows':len(rows),'weighted_total':weights,'duplicate_person_keys':0,'age_minus_one_n':sum(r['CH06']=='-1' for r in rows),'age_unknown_999_n':sum(r['CH06']=='999' for r in rows)}

def load_source(path,year):
 profiles=json.loads(REGISTRY_PATH.read_text());require(str(year) in profiles,'Unregistered source edition');profile=profiles[str(year)];raw=path.read_bytes()
 require(hashlib.sha256(raw).hexdigest()==profile['sha256'],'Source SHA-256 mismatch; revised editions require new review/profile')
 require(len(raw)==profile['bytes'],'Pinned source byte count mismatch')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  members=[x for x in z.infolist() if Path(x.filename).name==profile['persons_member']]
  require(len(members)==1,'Ambiguous/missing persons member');member=members[0]
  require(member.file_size<=250_000_000,'Oversized source member')
  reader=csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig')),delimiter=';')
  require(reader.fieldnames is not None and len(reader.fieldnames)==len(set(reader.fieldnames)),'Duplicate CSV columns')
  require(hashlib.sha256(';'.join(reader.fieldnames).encode()).hexdigest()==profile['columns_sha256'],'Pinned column layout mismatch')
  rows=list(reader)
 diagnostic=validate_rows(rows,year,profile);diagnostic.update(profile);diagnostic['source_member']=member.filename
 return rows,diagnostic

def aggregate(rows,age_policy='all',missing_policy='show_unknown',year=2025):
 require(age_policy in ('all','ages_1_17','ages_minus1_17'),'Unknown age policy')
 require(missing_policy in ('show_unknown','valid_responses'),'Unknown missing-data policy')
 counts=collections.Counter();sample=collections.Counter();selected=0
 for r in rows:
  age=integer(r['CH06'],'CH06');weight=integer(r['PONDERA'],'PONDERA');require(weight>0,'Nonpositive weight')
  if age_policy=='ages_1_17' and not 1<=age<=17:continue
  if age_policy=='ages_minus1_17' and not -1<=age<=17:continue
  selected+=1;g=birth_group(r['CH15']);counts[g]+=weight;sample[g]+=1
 denominator=sum(counts.values())-(counts['unknown'] if missing_policy=='valid_responses' else 0)
 require(denominator>0,'Empty denominator')
 groups=list(LABELS) if missing_policy=='show_unknown' else list(LABELS)[:3]
 result=[{'category':g,'label':LABELS[g],'numerator':counts[g],'denominator':denominator,'value':float(Decimal(counts[g])*100/Decimal(denominator)),'sample_n':sample[g],'missing_policy':missing_policy,'age_policy':age_policy,'year':year,'period':'T3','geo_code':'00','geo_scope':'EPH_total_urbano','unit':'PORCENTAJE','status':'candidate_unapproved','child_age_semantics':'sensitivity_not_approved' if age_policy!='all' else 'not_applicable'} for g in groups]
 require(sum(counts[g] for g in groups)==denominator,'Category numerator partition does not reconcile')
 return result,{'sample_total':selected,'weighted_total':sum(counts.values()),'unknown_weight':counts['unknown'],'unknown_n':sample['unknown']}

def reconcile(output,db_path,source_year,reference_year=2025):
 D=sqlite3.connect('file:'+str(db_path.resolve())+'?mode=ro',uri=True)
 try:rs=D.execute("SELECT source_json FROM observations WHERE workbook='8_3bNNyAmigrantes_Losmigrantesenlasreasurbanas' AND indicator_id='1048' AND year=?",(reference_year,)).fetchall()
 finally:D.close()
 require(len(rs)==6,'Reference must contain six known composition records');comparison=[];used=set()
 for (raw,) in rs:
  r=json.loads(raw);population=r['APERTURA_NIVEL_1'];require(population in ('Población urbana','NNyA urbanos'),'Unexpected reference population')
  require(r['TIPO_DE_DATO']=='DISTRIBUCION' and str(r['UNIDAD_GEOGRAFICA_CODIGO'])=='00' and r['MES'] is None,'Unexpected reference scope')
  label=r['MODALIDAD_APERTURA_NIVEL_1'];require(label in list(LABELS.values())[:3],'Unknown reference birth label')
  key=(population,label);require(key not in used,'Duplicate reference dimensional key');used.add(key)
  age='all' if population=='Población urbana' else 'ages_minus1_17'
  for c in output:
   if c['age_policy']==age and c['label']==label:
    cross=source_year!=reference_year
    comparison.append({'population':population,'category':c['category'],'missing_policy':c['missing_policy'],'age_policy':age,'source_year':source_year,'reference_year':reference_year,'cross_period_diagnostic':cross,'tableau':r['VALOR'],'recomputed':c['value'],'difference_pp':c['value']-r['VALOR'],'matches_one_decimal':matches_decimal(c['numerator'],c['denominator'],r['VALOR']),'eligibility':'not_equivalent_period' if cross else 'pending_child_age_semantics' if age!='all' else 'pending_recipe_and_edition_review'})
 require(len(comparison)==12,'Reference reconciliation coverage mismatch')
 return comparison

def run(input_path,db_path,out,year=2025,reference_year=2025):
 require(not out.exists(),'Output must be a new directory; previous versions are immutable')
 rows,source=load_source(input_path,year);output=[];diagnostics={}
 for age in ('all','ages_minus1_17','ages_1_17'):
  for missing in ('show_unknown','valid_responses'):
   rs,d=aggregate(rows,age,missing,year)
   for record in rs:
    record.update(source_sha256=source['sha256'],source_url=source['source_url'],domain_status='declared_total_urban' if age=='all' else 'age_semantics_pending',uncertainty_status='not_estimated_design_required')
   output+=rs;diagnostics[age+'/'+missing]=d
 comparison=reconcile(output,db_path,year,reference_year)
 # All input/semantic checks precede creation. Directory creation is exclusive.
 out.mkdir(parents=True,exist_ok=False)
 def write(name,obj):
  with (out/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)
 write('candidate_migration_national.json',output);write('reconciliation.json',comparison)
 with (out/'reconciliation.csv').open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
 write('diagnostics.json',{'source':source,'codebook_url':DOC_URL,'groups':diagnostics,'age_policy_note':'-1 was not explicitly labelled in the consulted official 2025 PDF/XLSX; child variants remain sensitivity only','comparison_period':{'source_year':year,'reference_year':reference_year},'release_status':'blocked_pending_semantic_review'})
 write('completion.json',{'status':'complete_candidate','source_year':year,'rows':len(rows),'aggregate_outputs':len(output),'comparison_records':len(comparison),'publication_approved':False})
 print('PASS candidate: source rows',len(rows),'aggregate outputs',len(output),'comparison records',len(comparison))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--database',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--source-year',type=int,choices=(2024,2025),default=2025);p.add_argument('--reference-year',type=int,default=2025);a=p.parse_args();run(a.input,a.database,a.out,a.source_year,a.reference_year)
