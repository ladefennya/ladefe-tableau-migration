# Migración LADEFE — Estadística social, económica y de programas

Revisión del 6 de noviembre de 2026 (Argentina). Estado: apto con reservas para desarrollar adaptadores; no validado para reemplazar datos publicados ni para habilitar comparaciones territoriales automáticamente.

## Resultado nuevo: el 101 % fue contrastado con microdatos oficiales

Se localizó en el HTML del portal de bases del INDEC el recurso de **EPH total urbano, tercer trimestre de 2025**, diferente de la EPH de 31 aglomerados. Descarga HTTP 200, 4.920.375 bytes. El archivo contiene hogares_tot.urb_3T_2025.txt y personas_tot.urb_3T_2025.txt. El hash completo está en fuente_ephu2025.json y results/diagnostics.json.

Fuente: https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_Tot_Urbano_3T_2025.zip
Portal: https://www.indec.gob.ar/Institucional/Indec/BasesDeDatos
Diseño: https://www.indec.gob.ar/ftp/cuadros/menusuperior/eahu/EPH_tot_urbano_estructura_bases_2025.pdf

La base de personas tiene 71.322 observaciones, todas en 2025/T3; ponderación total 43.337.370. No hay claves de persona duplicadas bajo CODUSU + AGLOMERADO + NRO_HOGAR + COMPONENTE. Se utilizó PONDERA para la composición por nacimiento, según el diseño para variables no monetarias. CH15 se agrupa: 1+2 misma provincia, 3 otra provincia, 4+5 otro país, 9 no sabe/no responde.

### Población urbana total: comparación independiente

| Categoría | Tableau 1048 | EPHU 2025: denominador de respuestas válidas | Diferencia aproximada |
|---|---:|---:|---:|
| En la provincia donde vive | 87,3 % | 86,470277 % | -0,829723 puntos |
| En otra provincia | 10,1 % | 9,973530 % | -0,126470 puntos |
| En otro país | 3,6 % | 3,556193 % | -0,043807 puntos |
| Total de las tres | 101,0 % | 100,000000 % | -1 punto |

Los casos CH15=9 son 14 observaciones y representan 11.318 personas ponderadas. Si se mantienen en el denominador, la terna es 86,447694 / 9,970926 / 3,555264 y debe mostrarse además 0,026116 % sin información. Por lo tanto, la diferencia de un punto no se explica por excluir/no excluir Ns/Nr.

La suma 101,0 tampoco puede atribuirse solamente al redondeo a un decimal de tres categorías exhaustivas: el error máximo conjunto sería 0,15 puntos porcentuales. **Se confirma que la terna guardada en Tableau no se reproduce a partir de esta edición pública bajo ninguna de las dos políticas de faltantes probadas.** No se identifica por ello el origen exacto (error de carga, edición distinta, ponderadores o filtro distinto). Es necesario registrar la consulta/código de la Defe antes de aprobar sustitución. Cambiar 87,3 por 86,3 solo para sumar 100 sería una corrección sin fundamento y no coincide con el reprocesamiento.

### NNyA y el tratamiento de la edad

Con selección -1 <= CH06 <= 17, y respuestas válidas a CH15, se obtiene 96,602342 / 2,617342 / 0,780316 %. Tableau presenta 96,7 / 2,6 / 0,8 %. También hay discrepancia de una décima en la primera categoría.

El archivo tiene 419 registros con CH06=-1. El diseño descargado describe CH06 como años cumplidos, pero no se corroboró una etiqueta explícita para -1 en el documento consultado. Por eso la selección que incluye -1 se entrega como **sensibilidad explícita**, no como universo infantil aprobado. Se conserva otra corrida para edades 1–17. La comparación principal de población total no depende de esta decisión sobre edad. Tampoco se ha aplicado un tratamiento especial a CH06=99: el universo total incluye todas las personas; una codificación de edad desconocida requeriría aclaración para indicadores por edad.

## Implementación y verificaciones

- ephu_migration_adapter.py es un CLI reproducible con biblioteca estándar de Python. Solo lee el ZIP público y la base maestra SQLite de referencia, sin modificarla.
- Rechaza salidas no vacías para preservar evidencias previas. Produce 21 agregados candidatos nacionales: dos políticas de faltantes y tres políticas de edad/sensibilidad. Cada registro conserva numerador, denominador, ponderación, período, muestra no ponderada, unidad y estado candidate_unapproved.
- Produce 12 comparaciones de las seis categorías de Tableau para ambas políticas de faltantes. No se fuerza equivalencia ni se transforma una diferencia en aprobación.
- Controla columnas, año/trimestre, pesos negativos, dominio de CH15, duplicación de claves, denominadores positivos y sumas de categorías.
- Seis pruebas unitarias aprobadas: ponderación y no respuesta; sensibilidad por edad; dominio inválido; peso negativo; políticas desconocidas; protección de salida existente. La corrida real aprobó controles estructurales también con Python -O: las validaciones de entrada usan ValueError, no assert.
- No estima errores estándar ni intervalos de confianza porque no se implementó aquí el diseño muestral completo. No se generaron estimaciones provinciales publicables ni geolocalización de personas.
- No redistribuye microdatos en el entregable: se incluyen únicamente código, evidencia agregada y enlace/hash de la fuente. La descarga original de trabajo está en /tmp/ephu2025_social.zip.

Reproducción:

```sh
python ephu_migration_adapter.py --input /ruta/EPH_Tot_Urbano_3T_2025.zip --database /ruta/base_maestra.sqlite --out /ruta/salida-candidata
python -m unittest discover -s . -p 'test_*.py'
```

## Contratos que deben preceder a la migración social/económica

El archivo contratos_sociales.csv contiene diez familias con unidad, regla de agregación, ponderación/denominador, representación territorial, potencial de automatización y referencia institucional. Son contratos técnicos propuestos que necesitan aprobación temática, no reglas inferidas automáticamente del nombre de un indicador.

1. **EPH/EPHU:** fijar universo y ponderador por indicador. En pobreza e ingresos, PONDERA no puede sustituir automáticamente PONDIH, PONDII o PONDII0; tampoco sumar la base de hogares después de unirla a personas sin controlar la multiplicación de filas. Documentar canastas/equivalencias, ingreso no respondido y período. EPHU total urbano no es toda la población del país y EPH de aglomerados no es EPHU.
2. **Censo:** separar personas, hogares y viviendas; la proporción de hogares con NBI no es la proporción de NNyA que viven en hogares con NBI. No sustituir NBI por IPMH. Guardar fuente/edición y universo de viviendas particulares. Los períodos intercensales no se completan con interpolaciones presentadas como datos oficiales.
3. **ANSES/BESS:** distinguir beneficio, liquidación, pago, titular y niño beneficiario; pueden superponerse programas. No sumar stocks mensuales ni calcular cobertura usando un denominador de otro universo. La edad y fecha de corte deben coincidir.
4. **PAE:** distinguir titulares vigentes, acumulados e incorporaciones. Un acumulado deduplicado no se obtiene sumando meses. El adaptador debe detectar revisiones históricas y publicar una nueva versión con trazabilidad, no solamente agregar el mes nuevo.
5. **Línea 102:** llamadas no son niños ni casos únicos. Comparación provincial exige cobertura, meses efectivamente informados y categorías homologadas. Cero, sin reporte y dato suprimido deben ser estados distintos.
6. **Protección y justicia:** separar personas, dispositivos, plazas, stock en fecha y flujo de entradas/salidas. SENAF, Defe y CNPT no necesariamente relevan el mismo universo. No interpretar presunto delito como condena ni duplicar personas que transitan por varios dispositivos. Para series de revisiones metodológicas, mostrar cortes/rupturas en lugar de una línea continua engañosa.
7. **Discapacidad:** distinguir prevalencia relevada y discapacidad certificada; CUD emitidos históricamente, personas registradas y CUD vigentes pueden ser poblaciones distintas. Grupos 15–19 no identifican 15–17; el backend debe rechazar un corte exacto de 0–17 si el insumo no lo permite.
8. **RENAPER:** población identificada con DNI y residencia declarada no equivale a población censada ni a la estimada en una encuesta. Lugar de nacimiento, país de origen y nacionalidad deben ser variables separadas. No completar edad con prorrateos quinquenales no publicados.
9. **Presupuesto:** conservar unidad monetaria, etapa del gasto y clasificador. Crédito inicial, vigente, devengado y pagado no son equivalentes. Nacional+provincial puede duplicar transferencias si no se consolida como la metodología oficial. El gasto etiquetado a niñez exige coeficientes de imputación explícitos y versionados; gasto público consolidado general no reemplaza GPSdN/ISPI.
10. **Precios, PIB y población:** usar deflactor/PIB/población con período y versión compatibles. Para flujos anuales no asumir IPC de diciembre; la elección del deflactor depende de la metodología aprobada. Diferenciar pesos, miles y millones y evitar deflactar dos veces series ya constantes. Por habitante requiere edad y población objetivo compatibles. No trasladar gasto administrativo a un mapa de beneficiarios sin una regla de territorialización.

## Organización y visualización recomendada

El mismo tema puede contener dimensiones incompatibles. Conviene una navegación por pregunta/derecho con una ficha técnica visible que indique población, territorio, período, unidad, fuente y estado. La ficha debe permitir cambiar entre valores absolutos y coberturas solo cuando exista un denominador aprobado; nunca usar un conmutador universal que invente esa relación.

Para EPH/EPHU, acompañar los mapas por advertencia de dominio y precisión; no sombrear municipios como si fueran estimados. Para gastos, mostrar series corrientes/constantes y participaciones con base definida; separar territorialización ejecutora de beneficiaria. Para protección/justicia, preferir agregados y comparaciones en tablas o pequeños múltiples; no localizar personas, domicilios o dispositivos sensibles sin autorización institucional.

Las fuentes institucionales se deben integrar mediante plantillas de entrega agregada validada, no depender de scraping frágil de portales ni de cuentas privadas de terceros. Toda automatización produce primero una versión candidata; cambios de esquema, universo o metodología pasan por revisión. No se enviaron correos, no se crearon accesos ni se publicaron cambios.

## Único próximo paso recomendado

Pedir o recuperar del equipo temático de la Defe la receta de cálculo/edición del indicador 1048 y la convención de edad; confrontarla con la salida candidata para aprobar su sustitución o documentar una diferencia de universo. En paralelo, el código ya permite repetir la comprobación sin volver a depender de Tableau como fuente única.
