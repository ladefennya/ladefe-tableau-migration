# Prototipo UX nativo — construcción portátil

Estado: propuesta para revisión supervisada. No es producto terminado, publicación aprobada, prueba con personas ni conformidad accesible certificada. El mapa sigue bloqueado por revisión cartográfica; los datos siguen siendo candidatos.

## Abrir y reconstruir desde la instantánea congelada

`index.html` ya incluye estilos, lógica y datos; puede servirse como archivo estático. No necesita SQLite, CSV, conexiones, APIs, fuentes o imágenes externas. Los enlaces a las fuentes originales son referencias para la persona, no dependencias de carga.

Para regenerar la misma propuesta se necesita únicamente Python3 estándar y los tres insumos incluidos:

```sh
python build_prototype.py \
  --data prototype_data.json \
  --template prototype_template.html \
  --contract state_contract.js \
  --out dist/index.html
```

El constructor no consulta bases ni carpetas de rondas anteriores. Escribe el HTML y `resources_manifest.json` al lado de la salida. El manifiesto registra SHA-256 del payload, plantilla, contrato y HTML; declara que no hay dependencias externas.

La instantánea incluida es la que se utilizó para el diseño revisado. Cambiar el código de interfaz no modifica sus observaciones. Sustituir el payload requiere una decisión y revisión nueva: no se actualizan datos automáticamente al reconstruir el HTML.

## Preparar otro payload desde artefactos explícitos

La preparación de datos está separada de la construcción del HTML. El operador elige todas las rutas; no hay rutas absolutas de workspace ni dependencia implícita de outputsR1.

```sh
python prepare_payload.py \
  --reference-db referencias/base_maestra.sqlite \
  --education-candidate candidatos/educacion/native_candidate.json \
  --health-candidate candidatos/salud/candidate.json \
  --health-summary candidatos/salud/reconciliation_summary.json \
  --migration-candidate candidatos/migraciones/candidate_migration_national.json \
  --out candidatos/prototype_data.json

python build_prototype.py \
  --data candidatos/prototype_data.json \
  --template prototype_template.html \
  --contract state_contract.js \
  --out dist/index.html
```

La preparación abre la base de referencia solo en lectura. Registra los hashes de los cinco insumos y del resultado en `<nombre_payload>_provenance.json`. Los objetos de datos conservan los títulos, unidades, períodos y estados del espécimen de diseño. Es una utilidad de preparación del prototipo acotado, no un adaptador genérico de fuentes nuevas ni una aprobación de equivalencias.

Requiere los esquemas que produjeron los adaptadores del equipo: observaciones educativas con período/grano/nivel, agregados sanitarios con códigos y marca map_eligible, resumen sanitario con hashes y categorías de migraciones con política de faltantes/edad. No deduce campos nuevos ni descarga fuentes. Cambiar años, universos, esquemas o la evidencia de conciliación requiere revisar el catálogo y los contratos; no basta pasar un archivo más reciente.

## Pruebas

```sh
node test_state_contract.js
```

Se comprobaron restauración por URL, rechazo por defecto de consultas inválidas, versión fijada, parámetros duplicados, ventanas temporales, comparación territorial, reinicio de dominio y ausencia de sustitución de universo. Se comprobó también que la preparación configurable reproduce el payload congelado sin diferencias, y que los scripts ya no contienen rutas locales absolutas.

`preview_tasks.json` contiene los recorridos para el navegador supervisado. El padre informó pruebas en escritorio y un iframe de390px (body375px) sin desborde horizontal global: comparador de dos provincias, ventana de serie independiente, historial, rechazo de?qv=99 y selección territorial coherente. También comunicó ajustes que se incorporaron: detalle de dos provincias, mensajes geográficos contextuales, etiquetas explícitas y edición legible. No se comprobó320px ni lector de pantalla. La limitación del selector automatizado getByLabel no se clasifica como fallo de accesibilidad: las etiquetas for/id están presentes y el acceso por rol funciona. La revisión visual final debe identificar el hash exacto del HTML; este README no sustituye ese registro. No hubo pruebas con personas.

La gramática singular se corrigió para «1 observación» en el caption y en el anuncio de estado. La compactación de filtros móviles queda como mejora posterior; no se modificó la disposición del diseño en este último ajuste de portabilidad.
