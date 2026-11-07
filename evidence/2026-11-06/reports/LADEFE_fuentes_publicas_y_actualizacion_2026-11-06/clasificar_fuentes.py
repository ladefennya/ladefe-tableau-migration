import csv,json,collections
from pathlib import Path
R=Path('/workspace/scratch/e1753b36d366/ladefe-master-v1');O=Path('/workspace/scratch/e1753b36d366/ladefe-public-evaluation')
rows=list(csv.DictReader(open(R/'diccionario_indicadores.csv',encoding='utf-8-sig')));bs=collections.defaultdict(list)
for r in rows:bs[r['workbook']].append(r)
U={
'educacion':'https://www.argentina.gob.ar/educacion/evaluacion-informacion-educativa/anuarios',
'indicadores_educativos':'https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/indicadores',
'vitales':'https://www.argentina.gob.ar/salud/deis/datos/defunciones',
'nacimientos':'https://www.argentina.gob.ar/salud/deis/datos/nacidosvivos',
'indec':'https://www.indec.gob.ar/Institucional/Indec/BasesDeDatos',
'censo':'https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165?lang=es',
'bess':'https://www.argentina.gob.ar/trabajo/seguridadsocial/bess',
'ennys':'https://datos.salud.gob.ar/dataset/ennys2',
'pae':'https://www.argentina.gob.ar/node/451503',
'linea':'https://www.argentina.gob.ar/capital-humano/familia/analisis-de-la-informacion-social/area-central-linea-102',
'penal':'https://datos.gob.ar/fr/dataset/desarrollo-social-dispositivos-aprehension-especializados-para-adolescentes-presuntos-infractores',
'proteccion':'https://www.argentina.gob.ar/noticias/el-ministerio-de-capital-humano-comienza-el-relevamiento-federal-de-ninos-y-adolescentes',
'fiscal':'https://www.argentina.gob.ar/node/230449',
'presupuesto':'https://www.presupuestoabierto.gob.ar/sici/datos-abiertos',
'cud':'https://www.argentina.gob.ar/andis/estadisticas/datos-estadisticos',
'renaper':'https://www.argentina.gob.ar/interior/renaper/transparencia/datosabiertos',
'progresar':'https://www.argentina.gob.ar/educaci%C3%B3n/progresar',
'food':'https://www.argentina.gob.ar/node/451131'}
def family(w):
 if w.startswith(('3_2','3_3','3_4')):return ('Educación RA e indicadores','alta candidata','anual al publicarse','educacion|indicadores_educativos','Cuadro exacto, nivel, modalidad, edad y gestión. Indicadores de egreso/escolarización pueden requerir fórmula y denominador adicional; microdatos escolares no siempre descargables sin acceso autorizado.')
 if w.startswith(('4_2a','4_2b','4_2c','4_3','4_4','7_1','7_3')):return ('Estadísticas vitales','alta candidata','anual al publicarse','vitales|nacimientos','Verificar año de ocurrencia/registro, residencia/hecho, edad, causa CIE y agrupamientos. Tasas requieren nacidos vivos o población compatible; algunas edades exactas no se recuperan de grupos publicados.')
 if w.startswith(('1_2','2_1a','2_1b','2_5c','2_5d','3_1b','3_5b','4_1','8_3b')):return ('EPH / EPH total urbano y fuentes mixtas','media-alta condicionada','trimestral o tercer trimestre anual según universo','indec|censo','No sustituir EPHU por 31 aglomerados. Fijar ponderador, población 0–17/0–19, cobertura y variables. Pobreza requiere ingreso, canastas, equivalencias y tratamiento de faltantes; salud incluye rama censal.')
 if w.startswith(('1_1','2_1NBI','2_5a','2_5b','2_6a','3_1a','3_5a','8_2','8_3a')):return ('Censo y cruces censales','verificación alta; actualización eventual','nuevos cuadros, revisiones o nuevo censo','censo|indec','Priorizar cuadros publicados; los cruces no publicados pueden necesitar REDATAM o procesamiento especial. No interpolar entre censos. Indígenas incluye también información EANNA.')
 if w.startswith(('2_6b','4_2d','4_6','8_1c')):return ('Encuestas especiales','reproceso histórico; no actualización periódica demostrada','solo nueva edición comparable','ennys|indec','EANNA 2016–2017, ENNyS2 2018–2019 y discapacidad 2018. Comprobar dominios muestrales y ponderadores. Metadato anual no implica una encuesta anual.')
 if w.startswith('2_2'):return ('Seguridad social ANSES/BESS','media condicionada','trimestral nacional; jurisdiccional según BESS','bess','Conciliar beneficios, titulares, personas y liquidaciones; frecuencia nacional/provincial distinta. Coberturas requieren denominador compatible.')
 if w.startswith('2_3'):return ('Prestaciones alimentarias','media-baja sin exportación estable probada','por publicación del programa','food|bess','Diferenciar personas, hogares, titulares y prestaciones; cambios de programa y nombre pueden romper series. No se verificó archivo actual equivalente por cada indicador.')
 if w.startswith('5_1'):return ('Cuidados y medidas de protección','manual o semiautomática','relevamientos publicados','proteccion','No reemplazar relevamientos Defe/CNPT con SENAF si universo, fecha y dispositivos difieren. Nuevo relevamiento 2025 anunciado en 2026; no implica base final ya disponible.')
 if w.startswith('5_2'):return ('PAE','media condicionada','mensual en la publicación actual','pae','Fuente actual describe titulares vigentes/acumulados, altas e inversión; exportación estable pendiente. No sumar titulares de meses sucesivos. Releer historia por revisiones.')
 if w.startswith('5_3'):return ('Línea 102','media condicionada','mensual en la publicación actual','linea','Respetar faltantes provinciales, motivo principal y cambios de homologación. Catálogo histórico no garantiza actualización actual; exportación pendiente.')
 if w.startswith('5_4'):return ('Justicia juvenil','semiautomática condicionada','por relevamiento','penal','CSV público histórico de aprehensión no sustituye el stock ni todos los dispositivos. Otros indicadores pueden venir de PDF; comprobar fecha, flujo/stock y definiciones.')
 if w.startswith('6_1'):return ('Presupuesto nacional e infancia','media-alta condicionada','mensual/trimestral con corte aprobado','presupuesto|fiscal','API puede requerir token; usar descargas abiertas cuando alcancen. Etiquetado infancia, clasificadores, devengado/pagado, inflación y PIB deben versionarse.')
 if w.startswith('6_2'):return ('Inversión consolidada en niñez/primera infancia','media-alta condicionada','por nueva edición del estudio','fiscal','Hojas oficiales GPSdN/ISPI hasta 2024 publicadas en octubre 2026. Mantener metodología de imputación y edades; gasto consolidado general no es reemplazo equivalente.')
 if w.startswith('7_4'):return ('Progresar','manual hasta identificar recurso equivalente','por publicación comprobable','progresar','La página del programa no acredita una serie abierta con todas las edades/provincias de la Defe. Datos parciales no prueban continuidad automatizable.')
 if w.startswith('8_1'):return ('CUD y seguridad social','parcial; media-baja','por publicación del registro','cud|bess','Requiere corte 0–17, provincia, sexo y cruce de cobertura. Discapacidad certificada no equivale a prevalencia de discapacidad. Un tablero no declara fuente útil en el catálogo original.')
 if w.startswith('8_3c'):return ('Migración administrativa y matrícula','media condicionada','por nueva edición de cada registro','renaper|educacion','RENAPER cuenta población identificada; no es Censo ni EPH. Edades quinquenales no permiten siempre 0–17; rama educativa requiere RA.')
 raise ValueError(w)
out=[]
for w,rs in bs.items():
 f,p,period,keys,risk=family(w);out.append({'workbook':w,'familia':f,'indicadores':len(rs),'verificacion':'fuente pública localizada a nivel de familia; equivalencia exacta por indicador pendiente','automatizacion_potencial':p,'frecuencia_candidata':period,'fuentes_oficiales':' | '.join(U[k] for k in keys.split('|')),'condiciones_y_limites':risk,'vinculos_con_faltantes_documentales':sum(bool(r['missing_fields']) for r in rs),'estado':'evaluación de factibilidad; adaptador no implementado'})
with open(O/'matriz_fuentes_71.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
summary=collections.Counter(x['familia'] for x in out);(O/'resumen_familias.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(summary);print('total',len(out),'links',sum(x['indicadores'] for x in out));assert len(out)==71
(O/'fuentes.json').write_text(json.dumps(U,ensure_ascii=False,indent=2))
