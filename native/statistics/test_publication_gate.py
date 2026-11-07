import unittest,json,copy
from pathlib import Path
from publication_gate import evaluate,temporal_proposal,validate_decision,REQUIRED_CHECKS
O=Path(__file__).parent
class PublicationGateTests(unittest.TestCase):
 def contract(self):return {'view_id':'test.education.province','allowed_presentations':['map','table'],'allowed_aggregations':['published_value'],'required_context':['source_sha256','snapshot','indicator_id','reference_period']}
 def context(self):return {'view_id':'test.education.province','source_sha256':'0'*64,'snapshot':'test','indicator_id':'test','reference_period':'2024–2025','checks':dict({k:'passed' for k in REQUIRED_CHECKS},geometry_topology='passed'),'presentation':'map','aggregation':'published_value','contrast_status':'matched_raw_rounding'}
 def test_unknown_fields_and_checks_fail_closed(self):
  c=self.context();c['viewid']='typo'
  with self.assertRaises(ValueError):evaluate(self.contract(),c)
  c=self.context();c['checks']['reference_peroid']='passed'
  with self.assertRaises(ValueError):evaluate(self.contract(),c)
  v=self.contract();v['requires_known_denomintor']=False
  with self.assertRaises(ValueError):evaluate(v,self.context())
 def test_invalid_geometry_blocks_map_only(self):
  c=self.context();c['checks']['geometry_topology']='failed';self.assertFalse(evaluate(self.contract(),c)['preview_allowed']);c['presentation']='table';self.assertTrue(evaluate(self.contract(),c)['preview_allowed'])
 def test_unknown_view_fails_closed(self):self.assertFalse(evaluate(None,{})['publication_allowed'])
 def test_exact_contrast_never_autoapproves(self):
  x=evaluate(self.contract(),self.context());self.assertTrue(x['preview_allowed']);self.assertFalse(x['publication_allowed']);self.assertIn('exact_scope_thematic_approval_missing',x['reasons'])
 def test_unknown_period_blocks_preview(self):
  c=self.context();c['checks']['reference_period']='unresolved';self.assertFalse(evaluate(self.contract(),c)['preview_allowed'])
 def test_average_not_implicitly_allowed(self):
  c=self.context();c['aggregation']='AVG';self.assertIn('aggregation_not_allowed:AVG',evaluate(self.contract(),c)['reasons'])
 def test_rounding_path_needs_evidence(self):
  c=self.context();c['contrast_status']='matched_source_display_rounding';self.assertFalse(evaluate(self.contract(),c)['preview_allowed']);c['rounding_rule_evidence']={'format':'0.00','first':'HALF_UP to 2 decimals','then':'HALF_UP to 1 decimal'};self.assertTrue(evaluate(self.contract(),c)['preview_allowed'])
 def test_denominator_total_cannot_replace_eligible(self):
  v=self.contract();v.update(requires_known_denominator=True,allowed_denominator_rules=['specified_weight']);c=self.context();c['denominator_rule']='all_births';self.assertIn('denominator_not_approved',evaluate(v,c)['reasons'])
 def test_fake_approval_without_identity_rejected(self):
  with self.assertRaises(ValueError):validate_decision({'state':'approved'})
 def test_approval_different_hash_not_reused(self):
  c=self.context();c['checks'].update(tableau_rendered='passed',accessibility='passed',source_methodology='passed');scope={k:c.get(k) for k in ('source_sha256','snapshot','view_id','indicator_id','reference_period')};scope['source_sha256']='another';decision={'state':'approved','approver':'synthetic_test_fixture','approved_at':'test','evidence':'synthetic','scope':scope};self.assertFalse(evaluate(self.contract(),c,decision)['publication_allowed'])
 def test_survey_domain_and_precision_enforced(self):
  v=self.contract();v['survey']=True;c=self.context();c['domain_status']='unsupported';c['uncertainty_status']='not_estimated_disclosed';self.assertFalse(evaluate(v,c)['preview_allowed']);c['domain_status']='supported';self.assertTrue(evaluate(v,c)['preview_allowed'])
 def test_real_20_rows_preserve_source_and_limit_period_derivation(self):
  rows=json.loads((O/'temporal_decisions.json').read_text())['records'];self.assertEqual(len(rows),20);census=0;unresolved=0
  for r in rows:
   raw=copy.deepcopy(r['raw_source']);p=temporal_proposal(raw,r['workbook']);self.assertEqual(raw,r['raw_source']);self.assertEqual(p['raw_source'],raw);self.assertFalse(p['effective_period_approved']);self.assertFalse(p['temporal_axis_supported'])
   if r['workbook']=='4_1Coberturadesalud':census+=1;self.assertEqual(p['reference_period_candidate'],int(raw['MODALIDAD_APERTURA_NIVEL_2']))
   else:unresolved+=1;self.assertIsNone(p['reference_period_candidate'])
  self.assertEqual((census,unresolved),(8,12))
 def test_real_xml_has_year_filters_not_temporal_axes(self):
  r=json.loads((O/'temporal_decisions.json').read_text())['records'][0]
  for ws in r['decision']['evidence']['worksheets']:
   self.assertTrue(ws['year_filters']);self.assertTrue(all('ANIO' not in (v or '') for v in ws['shelves'].values()))
 def test_reused_ids_do_not_normalize_other_workbook(self):
  raw=copy.deepcopy(json.loads((O/'temporal_decisions.json').read_text())['records'][0]['raw_source']);p=temporal_proposal(raw,'another_workbook');self.assertIsNone(p['reference_period_candidate'])
 def test_changed_census_dimension_rejected(self):
  raw=copy.deepcopy(json.loads((O/'temporal_decisions.json').read_text())['records'][0]['raw_source']);raw['MODALIDAD_APERTURA_NIVEL_2']='2030'
  with self.assertRaises(ValueError):temporal_proposal(raw,'4_1Coberturadesalud')
if __name__=='__main__':unittest.main()
