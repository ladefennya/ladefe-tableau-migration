# LADEFE — Adaptadores y contratos para tableros nativos

Estado: candidatos de migración, sin aprobación temática ni publicación. El informe integrado está en [Decisiones del equipo](../docs/native-migration/DICTAMEN_EQUIPO_2026-11-06.md). No se reemplazan `results/latest/`, la base maestra ni el demo con estas salidas.

## Dependencias y pruebas

Python 3.12 y openpyxl para el adaptador educativo; los otros adaptadores usan biblioteca estándar. El equipo probó openpyxl en el runtime disponible. No hay llamadas de escritura a servicios ni instalación/creación de bases remotas.

```sh
python -m pip install -r native/education/requirements.txt
python -m unittest discover -s native/education -p 'test_*.py' -v
python -m unittest discover -s native/health -p 'test_*.py' -v
python -m unittest discover -s native/social -p 'test_*.py' -v
node --test tests/*.test.js
python scripts/validate_demo.py
```

Las pruebas se ejecutan sin descargar datos. Para ejecutar conciliación con datos reales se requieren la base maestra de la extracción y los recursos oficiales documentados por cada adaptador. Estos archivos no se incluyen en Git. Los outputs completos son resultados separados; no deben agregarse a commits. La fecha/ciclo pertenece a la fuente: los adaptadores no inventan períodos nuevos.

## Ejecución de candidatos

Ejemplos desde la raíz, usando rutas propias y un destino nuevo por ejecución:

```sh
python native/education/education_adapter.py --source-zip /ruta/abandono.zip --reference-db /ruta/base_maestra.sqlite --out /ruta/candidatos/educacion-v1
python native/health/vital_adapter.py --births /ruta/nacimientos_2024.csv --deaths /ruta/defunciones_2024.csv --reference-db /ruta/base_maestra.sqlite --out /ruta/candidatos/salud-v1
python native/social/ephu_migration_adapter.py --input /ruta/EPH_Tot_Urbano_3T_2025.zip --database /ruta/base_maestra.sqlite --out /ruta/candidatos/ephu-v1
```

El adaptador DEIS está fijado a edición 2024 y hashes oficiales. No usar con otros años. Una nueva edición necesita un contrato y una nueva conciliación; un CSV legible no prueba que sea del año esperado.

Cada salida conserva valores, procedencia y estados candidatos. Conflictos de período, diferencias o falta de ficha se resuelven mediante revisión documentada; no se corrigen cambiando tolerancias, normalizando a100 ni recortando negativos.

## Auditorías de solo lectura

```sh
python native/statistics/review_statistics.py --database /ruta/base_maestra.sqlite --repo . --twb-root /ruta/definiciones_extraidas --out /ruta/revision-estadistica
python native/geography/audit_geography.py --database /ruta/base_maestra.sqlite --geojson demo/provincias.geojson --out /ruta/revision-gis
python native/ux/inspect_ux_evidence.py --database /ruta/base_maestra.sqlite --demo demo --out /ruta/evidencia-ux.json
```

La revisión UX es estática. No sustituye el prototipo y la vista previa supervisada con sites-preview y cua_repl antes de publicar cambios de interfaz. No se certificaron pruebas con personas, accesibilidad ni equivalencia visual.

## Alcance de los resúmenes

- Educación:85 referencias,84 coincidencias numéricas;15 de ellas tienen etiqueta temporal conflictiva;1 diferencia adicional. No llamar a eso84 vistas aprobadas.
- Salud:121 casos con componentes exactos; la ficha de denominadores y la interfaz aún necesitan aprobación.
- EPHU: discrepancia reproducible en migraciones; el reproceso es candidato, no reemplazo automático.
- GIS:51 de71 colecciones tienen MAPA y8 indicadores de apertura tienen candidaturas adicionales; compartir provincia o unidad no habilita asociar medidas.

Los contratos JSON son propuestas versionadas de metadatos y gates, no un motor de publicación automático ya implementado. El diseño prioriza liberación por indicador/vista, conservando versiones aprobadas y aislando las que requieren revisión.

## Segunda ronda de refinamiento

El estado actual y las correcciones están en [Refinamiento, ronda 2](../docs/native-migration/REFINAMIENTO_RONDA2.md). Hay 60 pruebas Python (incluye 15 del gate) y ocho archivos de pruebas JavaScript (siete del demo y el contrato de estado). Añadir a la lista de pruebas:

```sh
python -m unittest discover -s native/statistics -p 'test_*.py' -v
node native/ux/test_state_contract.js
```

El prototipo autocontenido está en [prototypes/native-review](../prototypes/native-review/README.md). Su mapa permanece bloqueado: la ronda 2 confirmó que la simplificación actual introduce geometrías inválidas. La inspección de coordenadas no sustituye validación topológica. Los scripts de geometría requieren GDAL/GEOS (probados con GDAL 3.10.3/GEOS 3.13.1 del entorno); son pruebas separadas de ingestión.

```sh
python native/statistics/create_evidence.py --database /ruta/base_maestra.sqlite --twb-root /ruta/definiciones_extraidas --out /ruta/decisiones-temporales
python native/geography/build_map_policy.py --database /ruta/base_maestra.sqlite --out /ruta/politicas-mapa
python native/geography/check_topology.py --geometry demo/provincias.geojson --out /ruta/topologia-demo
python native/geography/compare_source_geometry.py --source /ruta/ign_original.geojson --display demo/provincias.geojson --out /ruta/comparacion-geometria
python native/geography/check_boundary_cases.py --source /ruta/ign_original.geojson --display demo/provincias.geojson --out /ruta/fronteras
```

Usar un intérprete con osgeo para los tres últimos comandos. Los originales y la referencia no simplificada no se versionan en Git. El gate estadístico no autentica aprobadores ni puede aceptar decisiones sin un servicio institucional autorizado. Los pins de edición y las reglas de dominios se mantienen; una fuente nueva no se acepta modificando solo un hash esperado.
