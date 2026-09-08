# Paso 2 — Resultado del censo completo de 71 workbooks

Fecha: 2026-09-08  
Run: 34181187163

## Resultado ejecutivo

El escalado fue exitoso: **71 de 71 workbooks fueron descargados, abiertos e inventariados, sin fallas**.

La hipótesis central queda confirmada. LADEFE no tiene 71 soluciones técnicas diferentes: tiene una plataforma Tableau altamente estandarizada, con **dos familias estructurales**, de las cuales una concentra 69 workbooks.

Esto permite reemplazar Tableau mediante un motor común de indicadores y configuraciones por tablero, en vez de reconstruir 71 aplicaciones independientes.

## Cobertura técnica

- 71 workbooks y 71 extractos Hyper.
- 324.694.283 bytes descargados.
- 4.189 worksheets.
- 288 dashboards.
- 20.732 campos.
- 5.822 campos calculados.
- 17.537 filtros.
- 1.491 parámetros.
- 497 tablas Hyper.
- 961.554 filas Hyper inventariadas.
- Entre 12.951 y 14.984 filas físicas por workbook.
- 0 fallas de descarga o parseo.

## Familias encontradas

### F01 — plantilla estándar

- 69 workbooks.
- 59 worksheets.
- 4 dashboards.
- 292 campos.
- 82 campos calculados.
- 247 filtros.
- 21 parámetros.
- 7 tablas Hyper y 73 columnas físicas.

### F02 — variante con dashboards adicionales

- 2 workbooks:
  - `2_5aViviviendaCFCHabitacionales`
  - `7_3eMortalidadadolescenteSuicidios`
- Mantiene los mismos 59 worksheets, 292 campos, 82 cálculos, 247 filtros, 21 parámetros y esquema Hyper.
- La diferencia estructural principal es que contiene 6 dashboards en lugar de 4.
- Debe tratarse como variante de presentación, no como un backend diferente.

## Cobertura temática

| Eje del sitio | Workbooks |
|---|---:|
| Educación y cuidado | 20 |
| Condiciones de vida digna | 14 |
| Salud | 11 |
| Adolescencia | 8 |
| Grupos prioritarios | 7 |
| Protección de derechos y justicia juvenil | 6 |
| Inversión pública | 3 |
| Perfil demográfico | 2 |

## Duplicación y modelo de datos

No se encontraron archivos Hyper completamente idénticos a nivel binario. Esto es esperable: cada workbook contiene diferencias de datos, metadatos o versión.

Sí se encontraron **23 grupos de muestras repetidas**, entre ellos:

- `Configuracion`: idéntica en los 71 workbooks.
- geometría provincial: idéntica en los 71.
- grupos de indicadores, temas, indicadores y datos compartidos por numerosos workbooks.
- grandes conjuntos de workbooks con las mismas primeras filas de la tabla `Datos`.

La conclusión no es guardar un Hyper por tablero. Conviene construir:

1. una tabla canónica de datos;
2. catálogos únicos de temas, tableros, secciones, grupos e indicadores;
3. una geometría provincial única;
4. configuraciones de visualización por tablero;
5. reglas de deduplicación con claves sustantivas, no con hashes binarios del archivo completo.

## Decisión de arquitectura

La migración debe organizarse en dos capas:

### Backend común

Modelo federal normalizado basado en las 22 columnas de `Datos`, con claves para tema, tablero, sección, indicador, tipo de dato, período, unidad geográfica, aperturas, valor y valor auxiliar.

### Frontend configurable

Componentes reutilizables para:

- evolución temporal;
- distribución territorial y mapa;
- cruces relevantes;
- características;
- tablas;
- selectores de tema, tablero, sección e indicador.

Los 69 workbooks F01 usarán una configuración estándar. Los dos F02 añadirán una variante de layout con dashboards adicionales.

## Decisión sobre la migración

**La migración integral de los 71 tableros es técnicamente viable.**

El principal riesgo ya no es acceder a Tableau ni interpretar los workbooks. Los riesgos que quedan son:

- deduplicar correctamente los datos superpuestos;
- separar cálculos sustantivos de cálculos puramente visuales;
- identificar y automatizar las fuentes originales;
- validar equivalencia funcional y visual;
- establecer reglas de actualización para fuentes provinciales o no abiertas.

## Próximo paso

Construir el primer adaptador y producto funcional sobre la familia F01 usando Información censal como caso inicial. Luego conectar Pobreza, Matrícula secundaria, Natalidad y Justicia juvenil al mismo motor para demostrar reutilización transversal.

En paralelo, debe generarse una tabla canónica deduplicada de los 71 extractos y un catálogo de indicadores. Ese será el backend inicial del reemplazo.

## Actualización del gate semántico

La auditoría posterior del demo confirmó que la arquitectura reutilizable escala, pero también que no corresponde inferir automáticamente qué mapa y qué serie “acompañan” a cada indicador. La revisión de 127 solicitudes en seis pilotos habilitó provisionalmente tres familias conceptuales y bloqueó las asociaciones ambiguas. El detalle y el camino de aprobación están en `docs/VIEW_RELATION_REVIEW.md`.
