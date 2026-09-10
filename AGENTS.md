# AGENTS.md — LADEFE Tableau Migration

## Propósito del repositorio

Este repositorio contiene la prueba de factibilidad, ingeniería inversa y demo para reemplazar los tableros Tableau Public del Sistema de Monitoreo de LADEFE.

La cobertura técnica de 71/71 tableros demuestra que la arquitectura común puede analizarlos; no demuestra equivalencia estadística, validación temática ni preparación para producción.

## Alcance y límites

- Trabajar únicamente en `ladefennya/ladefe-tableau-migration` para este frente.
- No modificar otros repositorios o sitios de LADEFE sin autorización explícita.
- No presentar la demo como producto terminado.
- No afirmar equivalencia con Tableau sin una comparación reproducible de datos, filtros, cálculos y visualizaciones.
- No convertir automáticamente asociaciones candidatas en relaciones aprobadas.

## Disciplina Git

- Crear una rama desde el `main` vigente para cada objetivo.
- No escribir directamente en `main`.
- Verificar el SHA esperado antes de cada commit.
- Mantener cambios acotados y revisables.
- Abrir pull requests en borrador hasta completar las validaciones.
- No fusionar, desplegar ni ejecutar workflows de escritura sin autorización explícita.

## Ingeniería inversa y resultados

- Preservar la separación entre descarga, extracción, inventario, análisis `.hyper`, mapeo semántico y demo.
- Tratar `results/latest/` como salida reproducible del probe: no editar manualmente resultados para hacerlos coincidir con expectativas.
- Las salidas deben conservar trazabilidad al workbook, worksheet, dashboard, campo, filtro, parámetro, conexión o tabla de origen.
- Redactar atributos que puedan contener `password`, `token`, `secret`, cookies o credenciales.
- Limitar las muestras de datos al mínimo necesario para interpretar semántica y granularidad.
- No almacenar artifacts grandes o extractos completos en Git salvo decisión explícita y justificada.
- Ante un cambio de Tableau Public, fallar con diagnóstico claro y conservar la última salida válida.

## Contrato semántico

- Cada mapa y serie debe utilizar el indicador seleccionado o una relación explícita, versionada y curada en `demo/view-relations.json`.
- No inferir en el navegador indicadores “acompañantes”.
- Calcular porcentajes y tasas con denominador como ratio de sumas, conservando numerador y denominador o valor auxiliar.
- No promediar implícitamente territorios, aperturas o modalidades.
- Mostrar módulos temporales y territoriales solo cuando exista una vista propia o una relación curada de igual unidad.
- Identificar visualmente cuando una vista pertenece a un indicador relacionado.
- `scripts/build_view_mapping_review.py` puede proponer asociaciones, pero nunca aplicarlas automáticamente.
- Toda relación nueva debe pasar las validaciones de integridad, unidad y tipo de vista.

## Cobertura y validación

Mantener separados estos estados:

1. descubierto;
2. descargado;
3. extraído;
4. inventariado;
5. mapeado;
6. validado técnicamente;
7. validado estadísticamente;
8. validado por responsables temáticos;
9. listo para producción.

Nunca resumir todos esos estados con una sola cifra de cobertura.

## Demo y visualizaciones

- No forzar mapas para tableros sin dimensión territorial.
- Mantener correspondencia exacta entre dato, unidad, período, color, leyenda y tooltip.
- Verificar que los mapas no estén deformados y que las jurisdicciones se seleccionen correctamente.
- La evolución temporal debe ser visible solo cuando exista una serie compatible.
- Los selectores deben nombrar la entidad que el usuario elige: tablero, indicador, vista, territorio o período.
- Evitar numeraciones decorativas de indicadores si no comunican orden, etapa o referencia estable.
- Verificar escritorio, móvil, accesibilidad y estados sin datos.
- No exponer en el cliente la lógica privada de descubrimiento, descarga, limpieza, armonización o actualización.

## Pruebas mínimas

Antes de cerrar un cambio, ejecutar según corresponda:

- pruebas unitarias existentes;
- `scripts/validate_demo.py`;
- `scripts/audit_demo_semantics.py`;
- `tests/view_relations.test.js`;
- validación de integridad de CSV y JSON;
- comprobación de cobertura sin duplicados;
- comparación de al menos un caso testigo contra Tableau para cambios semánticos;
- revisión visual de mapa, serie, distribución, selectores y estados vacíos;
- diff completo contra `main`.

No reducir, omitir o suavizar una validación para obtener un resultado verde.

## GitHub Actions

- Usar versiones soportadas de las acciones y del runtime.
- Declarar permisos mínimos de manera explícita.
- Publicar artifacts con nombre, fecha, commit y criterios de retención claros.
- No imprimir URLs autenticadas ni secretos.
- Los resultados publicados en el repositorio deben provenir de una ejecución identificable y exitosa.
- Evitar que una ejecución parcial reemplace `results/latest/`.

## Criterio para escalar a 71 tableros

No recomendar migración masiva hasta que los cinco pilotos representen familias arquetípicas suficientes y cuenten con:

- fuente de reemplazo identificada;
- campos, cálculos, filtros y parámetros comprendidos;
- comparación reproducible con Tableau;
- excepciones documentadas;
- validación técnica y temática;
- estimación del trabajo automatizable y manual.

## Seguridad

- Nunca versionar credenciales, tokens, cookies, claves privadas, archivos `.env` ni URLs firmadas.
- No publicar datos no públicos recibidos de LADEFE o de las provincias.
- Separar claramente datos públicos, datos restringidos y datos de demostración.
- Mantener secretos fuera del frontend, artifacts y logs.

## Entrega

El cierre debe informar:

- archivos y familias de tableros afectados;
- estado de cobertura antes y después;
- pruebas ejecutadas y resultados;
- diferencias conocidas respecto de Tableau;
- elementos pendientes de validación temática;
- enlace al pull request;
- único próximo paso recomendado.
