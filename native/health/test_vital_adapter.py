import tempfile,unittest,subprocess,sys
from pathlib import Path
from vital_adapter import aggregate,load,BIRTH_COLS,validate_release_hash
class VitalAdapterTests(unittest.TestCase):
 def b(self,weight='5.2000 a 2499',gest='5.32 a 36',count=1,geo='02'):
  return dict(PROVRES=geo,TIPPARTO='1',SEXO='1',IMEDAD='2.15 a 19',ITIEMGEST=gest,IMINSTRUC='3.Primaria/C. EGB Completa',IPESONAC=weight,CUENTA=count)
 def d(self,age,count=1,geo='02'):
  return dict(PROVRES=geo,SEXO='1',CAUSA='P07',MAT='NULL',GRUPEDAD=age,CUENTA=count)
 def test_2000_to_2499_is_low_weight_but_2500_not(self):
  x=aggregate([self.b(count=7),self.b('6.2500 a 2999',count=3)],[])[0]
  self.assertEqual(x['low_birth_weight'],7);self.assertEqual(x['births'],10)
 def test_unknown_weight_and_gestation_are_not_zero_or_known(self):
  x=aggregate([self.b(count=2),self.b('9.Sin especificar','8.Sin especificar',count=3)],[])[0]
  self.assertEqual(x['births'],5);self.assertEqual(x['known_weight_births'],2);self.assertEqual(x['known_gestation_births'],2)
  self.assertEqual(x['low_birth_weight_pct_known_weight'],100);self.assertEqual(x['low_birth_weight_pct_all_births'],40)
 def test_unspecified_under_one_is_infant_not_allocated_neonatal(self):
  x=aggregate([self.b(count=1000)],[self.d('01.0 a 6 días',2),self.d('03.28 días a 11 meses',3),self.d('031. Menor de 1 año – Sin especificar',4)])[0]
  self.assertEqual(x['infant'],9);self.assertEqual(x['neonatal'],2);self.assertEqual(x['postneonatal'],3);self.assertEqual(x['infant_unspecified_age'],4)
 def test_nonprovincial_codes_preserved_not_mapped(self):
  x=aggregate([self.b(geo='99')],[])[0];self.assertEqual(x['province_code'],'99');self.assertFalse(x['map_eligible'])
 def test_population_rate_not_fabricated(self):
  x=aggregate([self.b()],[])[0];self.assertNotIn('birth_rate_per_1000_population',x)
 def test_schema_drift_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bad.csv';p.write_text('PROVRES;COUNT\n02;1\n')
   with self.assertRaises(ValueError):load(p,BIRTH_COLS)
 def test_schema_drift_rejected_under_optimized_python(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bad.csv';p.write_text('PROVRES;COUNT\n02;1\n')
   result=subprocess.run([sys.executable,'-O','-c',"from pathlib import Path;from vital_adapter import load,BIRTH_COLS;load(Path("+repr(str(p))+"),BIRTH_COLS)"],capture_output=True,text=True,cwd=Path(__file__).resolve().parent)
   self.assertNotEqual(result.returncode,0);self.assertIn('ValueError',result.stderr)
 def test_cli_default_hash_rejects_unpinned_file_before_tagging_2024(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'synthetic.csv';p.write_text('PROVRES;COUNT\n02;1\n')
   r=subprocess.run([sys.executable,'vital_adapter.py','--births',str(p),'--deaths',str(p),'--out',str(Path(t)/'out')],capture_output=True,text=True,cwd=Path(__file__).resolve().parent)
   self.assertNotEqual(r.returncode,0);self.assertIn('Unapproved release',r.stderr);self.assertFalse((Path(t)/'out').exists())
 def test_new_weight_category_is_not_counted_as_known(self):
  with self.assertRaises(ValueError):aggregate([self.b('10.Nueva categoría')],[])
 def test_new_gestation_category_is_not_counted_as_known(self):
  with self.assertRaises(ValueError):aggregate([self.b(gest='0.Desconocido nuevo')],[])
 def test_new_age_group_fails_instead_of_omitting_infant(self):
  with self.assertRaises(ValueError):aggregate([self.b()],[self.d('00.Menor1 nuevo')])
 def test_maternal_M_T_S_not_merged(self):
  rows=[dict(self.d('12.25 a 29',2),MAT='M'),dict(self.d('12.25 a 29',3),MAT='T'),dict(self.d('12.25 a 29',4),MAT='S')]
  x=aggregate([self.b(count=1000)],rows)[0];self.assertEqual(x['maternal_deaths'],2);self.assertEqual(x['late_maternal_deaths'],3);self.assertEqual(x['maternal_sequelae'],4)
 def test_empty_source_is_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'empty.csv';p.write_text(';'.join(BIRTH_COLS)+'\n')
   with self.assertRaises(ValueError):load(p,BIRTH_COLS)
 def test_sex_code3_preserved_but_not_semantically_labelled(self):
  r=self.b(count=2);r['SEXO']='3';x=aggregate([r],[])[0];self.assertEqual(x['births'],2)
 def test_hash_override_cannot_bypass_release_contract(self):
  import hashlib
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'unapproved.csv';p.write_text('different2024revision')
   with self.assertRaises(ValueError):validate_release_hash('births',p,hashlib.sha256(p.read_bytes()).hexdigest())
 def test_unrecognized_sex_code_fails_closed(self):
  r=self.b();r['SEXO']='0'
  with self.assertRaises(ValueError):aggregate([r],[])
if __name__=='__main__':unittest.main()
