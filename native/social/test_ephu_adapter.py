import unittest,tempfile
from pathlib import Path
from ephu_migration_adapter import aggregate,birth_group,run
class Tests(unittest.TestCase):
 def test_weights_and_missing(self):
  rows=[{'CH06':'12','CH15':'1','PONDERA':'7'},{'CH06':'10','CH15':'4','PONDERA':'1'},{'CH06':'40','CH15':'9','PONDERA':'2'}]
  r,d=aggregate(rows);self.assertEqual(r[0]['value'],70);self.assertEqual(d['unknown_weight'],2);self.assertEqual(sum(x['value'] for x in r),100)
  r,d=aggregate(rows,missing_policy='valid_responses');self.assertEqual(r[0]['value'],87.5)
 def test_age_sensitivity(self):
  rows=[{'CH06':'-1','CH15':'1','PONDERA':'10'},{'CH06':'17','CH15':'3','PONDERA':'10'},{'CH06':'18','CH15':'4','PONDERA':'10'}]
  a,d=aggregate(rows,'ages_minus1_17');self.assertEqual(d['sample_total'],2)
  a,d=aggregate(rows,'ages_1_17');self.assertEqual(d['sample_total'],1)
 def test_invalid_domain_fails(self):
  with self.assertRaises(KeyError):birth_group('0')
 def test_negative_weight_fails(self):
  with self.assertRaises(ValueError):aggregate([{'CH06':'10','CH15':'1','PONDERA':'-1'}])
 def test_unknown_policies_rejected(self):
  with self.assertRaises(ValueError):aggregate([],age_policy='unapproved')
  with self.assertRaises(ValueError):aggregate([],missing_policy='impute_zero')
 def test_preserves_existing_output(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);(out/'evidence.txt').write_text('original')
   with self.assertRaises(ValueError):run(Path('/missing.zip'),Path('/missing.sqlite'),out)
   self.assertEqual((out/'evidence.txt').read_text(),'original')
if __name__=='__main__':unittest.main()
