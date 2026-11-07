# Entregas recuperadas — 6 de noviembre de 2026

Estado al 7/11/2026: inventario, documentación y scripts recuperados; **los seis ZIP todavía no están publicados en esta rama**. La revisión automática bloqueó su carga por posible contenido no público. El manifiesto describe los paquetes preparados; su presencia en este documento no acredita su publicación.

El código de los adaptadores, las dos rondas de revisión y el prototipo permanecen en el [PR #2](https://github.com/ladefennya/ladefe-tableau-migration/pull/2), rama `work/native-statistical-contracts-20261106`, HEAD verificado `780f13c314e005597feaba028eb779903cda6b9f`. Este respaldo parte de `main` (`371aaae89c8a91b499d6fac20aec6ff49da376e3`) y lo complementa. No fusiona ese PR ni modifica el observatorio.

## Inventario preparado

| ZIP | Bytes | Archivos | Contenido |
| --- | ---: | ---: | --- |
| LADEFE_validacion_y_bases_2026-11-06.zip | 38.229.985 | 173 | 71 extracciones por workbook, definiciones XML, catálogos, comprobaciones e informe |
| LADEFE_base_maestra_calidad_v1_2026-11-06.zip | 30.308.798 | 17 | SQLite, diccionarios, diferencias, hallazgos, constructores y verificación |
| LADEFE_fuentes_publicas_y_actualizacion_2026-11-06.zip | 17.541 | 8 | Matriz de fuentes públicas, pruebas y scripts de clasificación |
| LADEFE_evidencias_equipo_migracion_2026-11-06.zip | 961.563 | 24 | Primera ronda: agregados candidatos y conciliaciones |
| LADEFE_refinamiento_ronda2_evidencias_2026-11-06.zip | 40.429.780 | 35 | Segunda ronda: agregados, conciliaciones y geometría fuente IGN |
| LADEFE_prototipo_para_abrir.zip | 18.276 | 2 | Copia HTML autocontenida e instrucciones históricas |

Total: 109.965.943 bytes comprimidos y 259 archivos. `manifest.json` contiene tamaños y SHA-256 de cada ZIP y cada miembro. Se conservaron los paquetes separados para no sobrescribir resultados entre rondas.

`reports/` permite leer los informes y scripts recuperados sin abrir los ZIP. Conserva la redacción histórica: métricas y conclusiones preliminares no son el estado vigente por el solo hecho de estar archivadas. En particular, el informe de base maestra corrige el control inicial de documentación faltante; los informes de segunda ronda del PR #2 refinan las conclusiones temáticas de la primera.

## Resultado verificado nuevamente

La restauración local verificó los seis ZIP y sus 259 miembros. Se volvió a ejecutar `verify_master.py` contra la base SQLite y los 71 JSON de origen: 973.514 registros de procedencia, 14.156 observaciones, integridad SQLite y claves foráneas, resultado PASS. Esto es integridad y conservación, no certificación temática. `verification_recovery.json` registra esta ejecución.

El demo histórico conserva 14.016 observaciones. No se reemplazó `results/latest/`, no se mezclaron ambas instantáneas y no se trasladaron candidatos al sitio publicado.

## Procedencia y clasificación

- Base maestra y extracciones: el manifiesto de origen declara extracción pública de 71 Tableau Public; `source_downloads.json` conserva hashes de paquetes por workbook.
- Educación: el adaptador del PR #2 identifica `https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_abandono_interanual.zip`.
- Salud: agregados de archivos públicos DEIS 2024; el contrato versiona hashes y dominios. `death_dimensions_2024.csv` contiene conteos por provincia, sexo, grupo de edad y causa; no contiene nombres, documentos ni domicilios.
- Social: salidas agregadas del reproceso EPH total urbano 2024/2025. Los paquetes de evidencias no incluyen microdatos EPH.
- Cartografía: descarga pública WFS del IGN; el manifiesto del PR #2 registra URL, SHA-256 y 24 geometrías. El original es demasiado pesado para un frontend.
- Un barrido local de XML y textos no encontró atributos de contraseña/token/secret/cookie con contenido ni patrones de claves privadas, tokens GitHub o URLs firmadas. Es un control limitado, no una garantía universal.

La conservación de archivos grandes se justifica por el pedido explícito de registrar las bases y todas sus evidencias para continuidad por otras personas y sistemas. Los paquetes comprimidos mantienen la SQLite de 174 MB y el GeoJSON de 112 MB fuera de archivos individuales que excedan el límite de GitHub. La aprobación de la carga de los paquetes sigue pendiente tras el bloqueo automático.

## Uso cuando estén disponibles los ZIP

```sh
python scripts/restore_recovered_evidence.py
python scripts/restore_recovered_evidence.py --extract-to /ruta/nueva/respaldo
python /ruta/nueva/respaldo/LADEFE_base_maestra_calidad_v1_2026-11-06/verify_master.py \
  /ruta/nueva/respaldo/LADEFE_base_maestra_calidad_v1_2026-11-06 \
  /ruta/nueva/respaldo/LADEFE_validacion_y_bases_2026-11-06/source_tables
```

El restaurador falla si falta un ZIP o un hash no coincide; exige un destino inexistente y comprueba todo antes de extraer. No descarga datos ni ejecuta scripts incluidos. Los constructores históricos conservan rutas de su entorno original: adaptar sus constantes de entrada/salida antes de regenerar. La verificación independiente acepta rutas explícitas.

## Pendientes sustantivos

Siguen abiertos los conflictos temporales educativos y de comedores, la discrepancia de migraciones, decisiones sobre denominadores y dominios de salud, topología cartográfica y validación temática/funcional. La referencia IGN no habilita mapas automáticamente. El HTML se conserva como evidencia de la entrega anterior; esta tarea no modifica ni valida su diseño.

Próximo paso de este respaldo: completar la carga de los seis ZIP y verificar sus hashes desde un clon nuevo antes de considerar registrado el conjunto completo.
