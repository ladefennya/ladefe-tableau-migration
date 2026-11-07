"""Deterministic statistical gates. No writes, no automatic approvals, no authentication layer."""
from copy import deepcopy
import re
REQUIRED_CHECKS=('source_integrity','schema','granularity','universe','reference_period','geography','calculation','unknown_policy')
PASS={'passed','not_applicable_documented'}
CONTRAST_OK={'exact_components','matched_raw_rounding','matched_source_display_rounding','not_applicable_documented'}

CONTRACT_FIELDS={'view_id','allowed_presentations','allowed_aggregations','required_context','requires_known_denominator','allowed_denominator_rules','survey','period_rule','required_decision_state','authenticity_note'}
CONTEXT_FIELDS={'view_id','source_sha256','snapshot','indicator_id','reference_period','checks','presentation','aggregation','denominator_rule','domain_status','uncertainty_status','contrast_status','rounding_rule_evidence'}
KNOWN_CHECKS=set(REQUIRED_CHECKS)|{'tableau_rendered','accessibility','source_methodology','geometry_topology'}
PRESENTATIONS={'map','choropleth','proportional_symbols','bar','grouped_bar','line','table','small_multiples'}
AGGREGATIONS={'published_value','ratio_of_eligible_sums','weighted_disjoint_share','count_sum','none'}

def validate_contract(contract):
 unknown=set(contract)-CONTRACT_FIELDS
 if unknown:raise ValueError('Unknown contract fields: '+','.join(sorted(unknown)))
 for key in ('view_id','allowed_presentations','allowed_aggregations','required_context'):
  if not contract.get(key):raise ValueError('Missing contract field: '+key)
 if not set(contract['allowed_presentations'])<=PRESENTATIONS:raise ValueError('Unknown presentation in contract')
 if not set(contract['allowed_aggregations'])<=AGGREGATIONS:raise ValueError('Unknown aggregation in contract')
 if not set(contract['required_context'])<=CONTEXT_FIELDS:raise ValueError('Unknown required context field')
 for key in ('requires_known_denominator','survey'):
  if key in contract and type(contract[key]) is not bool:raise ValueError('Contract boolean must be typed: '+key)

def validate_decision(decision):
 if decision is None:return
 if decision.get('state') not in ('pending','approved','rejected'):raise ValueError('Unknown decision state')
 if decision['state']=='approved' and not all(decision.get(k) for k in ('approver','approved_at','evidence','scope')):raise ValueError('Approval must identify approver, date, evidence and exact scope')

def evaluate(contract,context,decision=None):
 """Publication/preview permissions for one view and immutable source scope.
 'approved' is a stored governance input, never inferred here. Caller must authenticate it.
 """
 validate_decision(decision)
 if not contract:return {'preview_allowed':False,'publication_allowed':False,'reasons':['unregistered_view']}
 validate_contract(contract)
 if set(context)-CONTEXT_FIELDS:raise ValueError('Unknown context fields')
 if context.get('view_id')!=contract['view_id']:raise ValueError('Contract/view mismatch')
 reasons=[]
 scope={k:context.get(k) for k in ('source_sha256','snapshot','view_id','indicator_id','reference_period')}
 if not re.fullmatch(r'[0-9a-f]{64}',str(context.get('source_sha256') or '')):reasons.append('invalid_source_sha256')
 for field in contract.get('required_context',[]):
  if context.get(field) in (None,''):reasons.append('missing_context:'+field)
 checks=context.get('checks',{})
 if set(checks)-KNOWN_CHECKS:raise ValueError('Unknown check names')
 for check in REQUIRED_CHECKS:
  if checks.get(check) not in PASS:reasons.append('check_not_passed:'+check)
 action=context.get('presentation')
 if action not in contract['allowed_presentations']:reasons.append('presentation_not_allowed:'+str(action))
 if action in ('map','choropleth','proportional_symbols') and checks.get('geometry_topology')!='passed':reasons.append('map_geometry_not_passed')
 if context.get('aggregation') not in contract['allowed_aggregations']:reasons.append('aggregation_not_allowed:'+str(context.get('aggregation')))
 if contract.get('requires_known_denominator') and context.get('denominator_rule') not in contract.get('allowed_denominator_rules',[]):reasons.append('denominator_not_approved')
 if contract.get('survey'):
  if context.get('domain_status')!='supported':reasons.append('survey_domain_not_supported')
  if context.get('uncertainty_status') not in ('estimated_from_design','not_estimated_disclosed'):reasons.append('survey_uncertainty_not_disclosed')
 if context.get('contrast_status') not in CONTRAST_OK:reasons.append('contrast_not_resolved:'+str(context.get('contrast_status')))
 # Double rounding can be a faithful description of the source display but not proof of historical Tableau processing.
 if context.get('contrast_status')=='matched_source_display_rounding' and not context.get('rounding_rule_evidence'):reasons.append('display_rounding_rule_missing')
 preview_ok=not reasons
 publication_reasons=list(reasons)
 for check in ('tableau_rendered','accessibility','source_methodology'):
  if checks.get(check) not in PASS:publication_reasons.append('publication_check_not_passed:'+check)
 approved=decision is not None and decision['state']=='approved' and decision.get('scope')==scope
 if not approved:publication_reasons.append('exact_scope_thematic_approval_missing')
 return {'preview_allowed':preview_ok,'publication_allowed':not publication_reasons,'reasons':publication_reasons,'scope':scope,'decision_state':None if decision is None else decision['state']}

def temporal_proposal(raw,workbook):
 """Only the specifically evidenced census comparison gets a candidate period.
 The raw payload is preserved. This returns a proposal, never a corrected source record.
 """
 raw=deepcopy(raw)
 result={'raw_source':raw,'raw_year':raw.get('ANIO'),'reference_period_candidate':None,'normalization_status':'unresolved','temporal_axis_supported':False,'effective_period_approved':False}
 if workbook=='4_1Coberturadesalud' and str(raw.get('INDICADOR_ID'))=='789' and str(raw.get('TABLERO_ID'))=='63' and raw.get('TIPO_DE_DATO')=='APERTURA':
  if raw.get('APERTURA_NIVEL_2')!='Año Censal' or raw.get('MODALIDAD_APERTURA_NIVEL_2') not in ('2010','2022'):raise ValueError('Census comparison schema changed')
  result.update(reference_period_candidate=int(raw['MODALIDAD_APERTURA_NIVEL_2']),normalization_status='explicit_census_dimension_candidate',period_role='categorical_comparison')
 elif workbook=='3_2eEstablecimientosEntregadealimentos' and str(raw.get('INDICADOR_ID'))=='465' and str(raw.get('TABLERO_ID'))=='68':
  result.update(normalization_status='requires_primary_cutoff_and_table',period_role='categorical_cross_section')
 return result
