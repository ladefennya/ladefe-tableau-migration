import unittest,tempfile,subprocess,sys
from pathlib import Path
from ephu_migration_adapter import aggregate,birth_group,run,validate_rows,matches_decimal
class Tests(unittest.TestCase):
 def record(self,**changes):
  r=dict(CODUSU='abc',NRO_HOGAR='1',COMPONENTE='1',AGLOMERADO='32',ANO4='2025',TRIMESTRE='3',PROVINCIA='02',CH06='12',CH15='1',PONDERA='7');r.update(changes);return r
 def test_weights_and_missing(self):
  rows=[self.record(),self.record(CH06='10',CH15='4',PONDERA='1'),self.record(CH06='40',CH15='9',PONDERA='2')]
  r,d=aggregate(rows);self.assertEqual(r[0]['value'],70);self.assertEqual(d['unknown_weight'],2);self.assertEqual(sum(x['value'] for x in r),100)
  r,d=aggregate(rows,missing_policy='valid_responses');self.assertEqual(r[0]['value'],87.5)
 def test_age_sensitivity_is_not_approved(self):
  rows=[self.record(CH06='-1',PONDERA='10'),self.record(CH06='17',CH15='3',PONDERA='10'),self.record(CH06='18',CH15='4',PONDERA='10')]
  a,d=aggregate(rows,'ages_minus1_17');self.assertEqual(d['sample_total'],2);self.assertEqual(a[0]['child_age_semantics'],'sensitivity_not_approved')
  a,d=aggregate(rows,'ages_1_17');self.assertEqual(d['sample_total'],1)
 def test_invalid_domain_fails(self):
  with self.assertRaises(ValueError):birth_group('0')
 def test_nonpositive_weight_fails(self):
  for weight in ['-1','0','NA','7.5']:
   with self.assertRaises(ValueError):aggregate([self.record(PONDERA=weight)])
 def test_unknown_policies_rejected(self):
  with self.assertRaises(ValueError):aggregate([],age_policy='unapproved')
  with self.assertRaises(ValueError):aggregate([],missing_policy='impute_zero')
 def test_preserves_existing_output(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);(out/'evidence.txt').write_text('original')
   with self.assertRaises(ValueError):run(Path('/missing.zip'),Path('/missing.sqlite'),out)
   self.assertEqual((out/'evidence.txt').read_text(),'original')
 def test_rejects_even_empty_existing_output(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):run(Path('/missing.zip'),Path('/missing.sqlite'),Path(tmp))
 def test_changed_hash_fails_before_output(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'arbitrary.zip';p.write_bytes(b'not an approved edition');out=Path(tmp)/'out'
   with self.assertRaisesRegex(ValueError,'SHA-256'):run(p,Path('/missing.sqlite'),out)
   self.assertFalse(out.exists())
 def test_checks_survive_optimized_python(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'arbitrary.zip';p.write_bytes(b'bad');out=Path(tmp)/'out'
   r=subprocess.run([sys.executable,'-O','ephu_migration_adapter.py','--input',str(p),'--database','/missing.sqlite','--out',str(out)],cwd=Path(__file__).parent,capture_output=True,text=True)
   self.assertNotEqual(r.returncode,0);self.assertIn('SHA-256',r.stderr);self.assertFalse(out.exists())
 def test_source_year_and_period_must_match(self):
  for r in [self.record(ANO4='2024'),self.record(TRIMESTRE='2')]:
   with self.assertRaises(ValueError):validate_rows([r],2025)
 def test_duplicate_keys_fail(self):
  with self.assertRaises(ValueError):validate_rows([self.record(),self.record()],2025)
 def test_pin_counts_and_weights(self):
  with self.assertRaises(ValueError):validate_rows([self.record()],2025,{'sample_rows':2,'weighted_total':7})
  with self.assertRaises(ValueError):validate_rows([self.record()],2025,{'sample_rows':1,'weighted_total':8})
 def test_geography_age_missing_and_identity_domains(self):
  for r in [self.record(PROVINCIA='00'),self.record(CH06='-2'),self.record(CH06='NA'),self.record(CODUSU=''),self.record(CH15='NA')]:
   with self.assertRaises(ValueError):validate_rows([r],2025)
 def test_tolerance_uses_exact_decimal_interval(self):
  self.assertTrue(matches_decimal(995,10000,10));self.assertFalse(matches_decimal(9949,100000,10))
  self.assertTrue(matches_decimal(1005,10000,10));self.assertFalse(matches_decimal(10051,100000,10))
if __name__=='__main__':unittest.main()
