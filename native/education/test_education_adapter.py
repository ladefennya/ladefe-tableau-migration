import io,json,sqlite3,tempfile,unittest,zipfile,subprocess,sys
from pathlib import Path
import openpyxl
from education_adapter import extract,reconcile,GEO,stable_key,rounded,format_decimals,map_reference

def fixture(path,bad_header=False,bad_nonapp=False):
 wb=openpyxl.Workbook();ws=wb.active;ws.title='2024-2025';ws.cell(10,1,'División Político Territorial');ws.cell(10,3,'Wrong' if bad_header else 'Primaria');ws.cell(10,11,'Secundaria');ws.cell(11,3,'Total');ws.cell(11,11,'Total')
 for ri,(label,(code,kind)) in enumerate(GEO.items(),12):
  ws.cell(ri,1,label);structure=None if kind=='national' else '6-6';
  if structure:ws.cell(ri,2,structure)
  for col in range(3,18):
   if structure=='6-6' and col==10:
    if bad_nonapp:ws.cell(ri,col,0)
   else:ws.cell(ri,col,-.1 if code=='38' and col==3 else 8.04719453540115 if kind=='national' and col==11 else 1.0)
 lim=wb.create_sheet('Limitaciones');lim['A1']='Closed-cohort model may produce negative dropout.'
 b=io.BytesIO();wb.save(b)
 with zipfile.ZipFile(path,'w') as z:z.writestr('Tasa 2025 según división político-territorial.xlsx',b.getvalue())

class AdapterTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.src=self.root/'source.zip';fixture(self.src)
 def tearDown(self):self.tmp.cleanup()
 def test_preserves_negative_and_nonapplicable(self):
  rs,meta=extract(self.src);self.assertEqual(len(rs),405);r=next(r for r in rs if r['geo_code']=='38' and r['level']=='primary' and r['grade_system']=='total');self.assertEqual(r['value'],-.1);self.assertEqual(r['period_label'],'2024-2025');self.assertIn('negative',meta['limitations']);missing=next(r for r in rs if r['geo_code']=='06' and r['level']=='primary' and r['grade_system']=='7');self.assertIsNone(missing['value']);self.assertEqual(missing['cell_status'],'not_applicable')
 def test_rejects_silent_layout_shift(self):
  fixture(self.src,bad_header=True)
  with self.assertRaises(ValueError):extract(self.src)
 def test_rejects_populated_nonapplicable_grade(self):
  fixture(self.src,bad_nonapp=True)
  with self.assertRaises(ValueError):extract(self.src)
 def test_invalid_schema_rejected_under_optimized_python(self):
  fixture(self.src,bad_header=True)
  code='from education_adapter import extract; extract('+repr(str(self.src))+')'
  result=subprocess.run([sys.executable,'-O','-c',code],capture_output=True,text=True,cwd=Path(__file__).parent)
  self.assertNotEqual(result.returncode,0);self.assertIn('Unexpected header',result.stderr)
 def test_value_revision_preserves_observation_identity(self):
  r=extract(self.src)[0][0];changed=dict(r,value=99);self.assertEqual(stable_key(r),stable_key(changed));changed=dict(r,period_end=2026);self.assertNotEqual(stable_key(r),stable_key(changed))
 def test_ambiguous_label_is_blocked_and_real_difference_not_rounded_away(self):
  p=self.root/'reference.sqlite';d=sqlite3.connect(p);d.execute('CREATE TABLE observations(workbook,indicator_id,source_json,observation_key)')
  common={'ANIO':2024,'UNIDAD_GEOGRAFICA_CODIGO':'00','MODALIDAD_APERTURA_NIVEL_1':'Total','APERTURA_DESCRIPCION':'2023/2024','VALOR':1.,'VALOR_AUXILIAR':None,'TIPO_DE_DATO':'APERTURA'}
  d.execute('INSERT INTO observations VALUES(?,?,?,?)',('3_3fMatrculaIEPromocinyabandono','380',json.dumps(common),'key1'))
  second=dict(common,MODALIDAD_APERTURA_NIVEL_1='Tasa de abandono interanual del nivel secundario',APERTURA_DESCRIPCION=None,VALOR=8.1,TIPO_DE_DATO='SERIE_TEMPORAL');d.execute('INSERT INTO observations VALUES(?,?,?,?)',('3_3fMatrculaIEPromocinyabandono','384',json.dumps(second),'key2'));d.commit();d.close()
  rs=reconcile(extract(self.src)[0],p);self.assertEqual(rs[0]['status'],'blocked_temporal_label_conflict');self.assertTrue(rs[0]['matches_one_decimal']);self.assertEqual(rs[1]['status'],'different_value');self.assertFalse(rs[1]['matches_one_decimal'])
 def test_exact_rounding_tie_policy(self):
  self.assertEqual(str(rounded('8.05')),'8.1');self.assertEqual(str(rounded('-0.05')),'-0.1');self.assertEqual(str(rounded('8.04719453540115')),'8.0');self.assertNotEqual(rounded('8.05'),rounded('8.0'))
 def test_cell_display_double_rounding_is_explicit(self):
  self.assertEqual(str(rounded(rounded('8.04719453540115',2))),'8.1');self.assertEqual(format_decimals('0.00'),2);self.assertIsNone(format_decimals(None));self.assertIsNone(format_decimals('0.00%'))
 def test_unknown_series_modality_is_not_secondary(self):
  with self.assertRaises(ValueError):map_reference('384',{'MODALIDAD_APERTURA_NIVEL_1':'New unknown label'})
 def test_unknown_grade_is_not_total(self):
  with self.assertRaises(ValueError):map_reference('380',{'MODALIDAD_APERTURA_NIVEL_1':'Sin clasificar'})
 def test_different_structures_cannot_overwrite_lookup(self):
  rs=extract(self.src)[0];rs.append(dict(rs[0],education_structure='7-5'));p=self.root/'reference.sqlite';d=sqlite3.connect(p);d.execute('CREATE TABLE observations(workbook,indicator_id,source_json,observation_key)');d.close()
  with self.assertRaisesRegex(ValueError,'Ambiguous candidate lookup'):reconcile(rs,p)
 def test_missing_map_scope_is_not_national(self):
  p=self.root/'reference.sqlite';d=sqlite3.connect(p);d.execute('CREATE TABLE observations(workbook,indicator_id,source_json,observation_key)');r={'ANIO':2024,'UNIDAD_GEOGRAFICA_CODIGO':None,'UNIDAD_GEOGRAFICA_NOMBRE':None,'TIPO_DE_DATO':'MAPA','VALOR':1,'VALOR_AUXILIAR':100};d.execute('INSERT INTO observations VALUES(?,?,?,?)',('3_3fMatrculaIEPromocinyabandono','381',json.dumps(r),'key'));d.commit();d.close()
  with self.assertRaisesRegex(ValueError,'Absent geographic scope'):reconcile(extract(self.src)[0],p)
 def test_national_grade7_has_explicit_structure(self):
  rs=extract(self.src)[0];p=next(r for r in rs if r['geo_code']=='00' and r['level']=='primary' and r['grade_system']=='7');s=next(r for r in rs if r['geo_code']=='00' and r['level']=='secondary' and r['grade_system']=='7');self.assertEqual(p['education_structure'],'7-5');self.assertEqual(s['education_structure'],'6-6');self.assertEqual(p['geo_education_structure'],'mixed')
 def test_cli_manifest_hashes_and_preserves_destination(self):
  out=self.root/'out';cmd=[sys.executable,'-O',str(Path(__file__).with_name('education_adapter.py')),'--source-zip',str(self.src),'--out',str(out)];r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
  import hashlib
  manifest=json.loads((out/'manifest.json').read_text())
  for name,digest in manifest['outputs'].items():self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),digest)
  first=(out/'manifest.json').read_bytes();r=subprocess.run(cmd,capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertEqual((out/'manifest.json').read_bytes(),first)
 def test_percent_scaled_cell_format_is_rejected(self):
  wb=openpyxl.Workbook();ws=wb.active;ws.title='2024-2025';ws.cell(10,1,'División Político Territorial');ws.cell(10,3,'Primaria');ws.cell(10,11,'Secundaria');ws.cell(11,3,'Total');ws.cell(11,11,'Total')
  for ri,(label,(code,kind)) in enumerate(GEO.items(),12):
   ws.cell(ri,1,label)
   if kind!='national':ws.cell(ri,2,'6-6')
   for col in range(3,18):
    if kind!='national' and col==10:continue
    ws.cell(ri,col,1.)
  ws.cell(12,3).number_format='0.00%';wb.create_sheet('Limitaciones');b=io.BytesIO();wb.save(b)
  with zipfile.ZipFile(self.src,'w') as z:z.writestr('2025 división político-territorial.xlsx',b.getvalue())
  with self.assertRaisesRegex(ValueError,'percent scale requires review'):extract(self.src)
if __name__=='__main__':unittest.main()
