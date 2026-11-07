# Piloto nativo — Abandono escolar interanual (tablero 3.3f, D.1 a D.5)

Estado: **candidato técnico para revisión de La Defe. No publicado, sin aprobación temática.**

Primer tablero llevado de punta a punta con el motor nativo: datos desde la fuente oficial, contrastados con Tableau, con mapa, ranking, serie, gráfico por grado y tabla coherentes entre sí. Abrir `index.html` en cualquier navegador; no tiene dependencias externas.

## Qué reemplaza

La sección de abandono interanual del tablero **3.3f. Matrícula de la Educación común. Indicadores educativos: Promoción efectiva y abandono escolar**:

| Tableau | Piloto |
|---|---|
| D.2 / D.4 · abandono primario y secundario por jurisdicción, solo último ciclo | Mapa y ranking por provincia para los 13 ciclos (2012-2013 a 2024-2025), escala de color común a todos los ciclos |
| D.5 · evolución por nivel, total país desde 2014-2015 | Serie 2012-2013 a 2024-2025, total país y una jurisdicción a elección |
| D.1 / D.3 · abandono por grado/año, total país | Por grado/año, total país y jurisdicción a elección; conflicto de rótulo visible |
| Sin tabla descargable | Tabla con valor exacto, valor visible de la planilla, valor de Tableau y estado de verificación; descarga CSV |

La sección de promoción efectiva (C.1 a C.5) queda para la próxima iteración: usa otra planilla de la misma fuente.

## Verificación

- **85 comparaciones contra Tableau:** 69 coinciden a un decimal, 1 coincide con doble redondeo (secundaria nacional 2023-2024: 8,05 visible → 8,1) y 15 quedan **bloqueadas** porque Tableau rotula «2023/2024» valores que en la planilla son del ciclo 2024-2025.
- Una misma cifra puede estar en dos vistas de Tableau con distinto resultado: el total nacional 2024-2025 coincide en la serie D.5 y está bloqueado en el gráfico por grado D.1/D.3. Por eso la verificación se guarda por vista.
- Los 4.844 valores restantes vienen de la planilla oficial y no tienen contraparte en Tableau (ciclos anteriores por provincia, grados por provincia).
- Pruebas: `python -m unittest discover -s prototypes/pilot-abandono -p 'test_*.py' -v` (9 pruebas: invariantes del payload, geometría, negativos, subdivisiones y paridad del redondeo HALF_UP entre JavaScript y Python en los 4.927 valores).
- Revisión visual con navegador sin interfaz a 1280 px y 390 px: sin errores de consola ni desborde horizontal. No reemplaza pruebas con personas ni una auditoría de accesibilidad.

## Reglas aplicadas

- Período = ciclo lectivo de la fuente, nunca año de carga.
- Valores tal como los publica la planilla; redondeo HALF_UP decimal solo para mostrar. No se promedian ni suman jurisdicciones.
- Negativos conservados, con nota metodológica de la fuente (modelo de flujo de sistema cerrado).
- Conurbano y Resto de Buenos Aires se muestran en la tabla, separados; no se mapean ni se suman.
- El color se asigna sobre el valor redondeado que se lee, para que dos provincias con el mismo número tengan el mismo color.
- Mapa con la geometría `native/geography/display/provincias_v2.geojson` (24/24 válidas, sin superposiciones, con Islas Malvinas). El constructor se niega a construir con una geometría no validada.

## Decisiones pendientes de La Defe

1. Rótulo del ciclo en D.1/D.3: confirmar que corresponde a 2024-2025 (como dice la planilla) y no a 2023/2024.
2. Tratamiento de los abandonos negativos en la presentación pública.
3. Si se amplía el alcance respecto de Tableau (13 ciclos por provincia, grados por provincia) o se mantiene el recorte original.
4. Mapa bicontinental: incluido por defecto (continente, Malvinas y recuadro con el sector antártico e islas del Atlántico Sur). Confirmar que el formato del recuadro es el adecuado.

## Reconstruir

```sh
python prototypes/pilot-abandono/prepare_pilot.py \
  --candidate /ruta/educacion/native_candidate.json \
  --reconciliation /ruta/educacion/reconciliation.json \
  --geometry native/geography/display/provincias_v2.geojson \
  --geometry-validation native/geography/display/validacion_provincias_v2.json \
  --inset native/geography/display/antartida_recuadro_v1.geojson \
  --out prototypes/pilot-abandono/pilot_data.json

python prototypes/pilot-abandono/build_pilot.py \
  --data prototypes/pilot-abandono/pilot_data.json \
  --template prototypes/pilot-abandono/pilot_template.html \
  --out prototypes/pilot-abandono/index.html
```

Las entradas del adaptador están en la entrega recuperada `LADEFE_refinamiento_ronda2_evidencias_2026-11-06` (PR #3), carpeta `education/`; se reconstruyen con `scripts/restore_recovered_evidence.py`. `pilot_data_provenance.json` registra los hashes de cada entrada.
