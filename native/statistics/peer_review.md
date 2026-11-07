# Segunda revisión estadística cruzada

Estado: revisión técnica de agentes; ninguna decisión temática humana aprobada. Se examinó el árbol de trabajo de `/tmp/ladefe-check` en la rama indicada por coordinación, los tres adaptadores nativos, sus pruebas/README y el dictamen integrado. No se modificó el repositorio ni la base original. Todos los archivos de esta subentrega están bajo `ladefe-team-round2/statistics/`.

## Resultados ejecutables

- `publication_gate.py`: decisión determinista por vista. No publica ni modifica datos. Vista no registrada, clave contractual desconocida, check mal escrito o agregación no permitida no pueden producir una autorización positiva. El SHA debe tener formato de64dígitos hexadecimales.
- `view_contracts.json`: seis contratos candidatos de vistas (abandono provincial, bajo peso, pretérmino, migraciones EPHU totales, comparación censal de cobertura y cruce de comedores). Estados propuestos, no aprobados.
- `temporal_decisions.json`:20 registros completos de la base, con propuesta semántica separada de dato crudo, identificador de observación, ID original, hash XML, shelves y filtros. Las20decisiones están pending, con aprobador/fecha nulos.
- `test_publication_gate.py`:15pruebas aprobadas, incluyendo conservación de20registros reales y evidencia estática de XML. Las pruebas de un flujo de aprobación usan fixtures sintéticos; no crean aprobación real.

## Lo temporal que puede y no puede normalizarse

### Salud789: ocho filas

La dimensión explícita `APERTURA_NIVEL_2=Año Censal` y su modalidad2010/2022 proporcionan un período candidato para una comparación categórica por edad. Los ocho `ANIO` secuenciales2022…2029 no son una serie temporal válida de esos porcentajes. Se puede construir una representación candidata que preserve `raw_year` y agregue `reference_period_candidate` desde esa dimensión, únicamente para el workbook/indicador/tablero comprobados. La función exige el workbook, para no reutilizar globalmente IDs locales.

Lo respaldado por el XML: las hojas `Cruces Relevantes - Aperturas y Grupos - Barras/Tabla` sitúan las dos modalidades en columnas/filas y usan `AVG(VALOR)` para barras. `ANIO` **sí aparece en filtros**, con enumeración all en la definición descargada; no figura como eje de esas dos hojas. Por tanto, puede afirmarse que el cruce se organiza por categorías; no que el año crudo sea irrelevante para toda interacción de Tableau. No se ejecutó el dashboard para probar sus filtros.

Estado: normalización candidata justificada por evidencia interna, no aprobación de período efectivo ni de producción. Falta cotejar valores/edición de Censo2010/2022 y comportamiento de la vista original. No publicar un eje2022–2029 ni llamar pronósticos a las filas.

### Comedores465: doce filas

La secuencia de `ANIO` cambia con Total/Urbano/Rural y nivel educativo, no con una serie. El XML muestra agrupación categórica y filtro de año, pero no acredita el corte estadístico común. No se deriva2024o2025 a partir de coincidencia de orden o valor. Los doce registros conservan período desconocido; bloquea una vista con fecha interpretativa o un filtro/año sin resolver. Se requiere el cuadro primario y la edición usada por la Defe.

### Educación380/382/384

La revisión de los15conflictos temporales debe conservar ciclo inicial/final y ambos textos (etiqueta antigua y edición que reproduce valores). La coincidencia numérica con2024–2025 no elimina la contradicción2023/2024 de las aperturas. El equipo educativo comunicó además que la celda nacional secundaria2023–2024 tiene valor subyacente8,0471945354 pero formato Excel de dos decimales: visualmente8,05; un segundo redondeo HALF_UPa una decimal produce8,1. Es una explicación determinista alternativa de la divergencia, **no prueba del proceso histórico de la Defe**. El gate admite un estado diferenciado `matched_source_display_rounding` solo si se documenta la regla; sigue requiriendo decisión de alcance y aprobación temática para publicar.

## Supuestos revisados y cambios solicitados a agentes

| Área | Riesgo o defecto | Resultado y acción |
|---|---|---|
| Educación | `abs(delta)<=0,05` se llamaba coincidencia a una decimal | Es compatibilidad con intervalo de precisión; los empates y el doble redondeo requieren política explícita. No ampliar tolerancia para ocultar8,04719vs8,1. Agente educativo separará comparación cruda y del valor mostrado. |
| Educación | Etiqueta desconocida en384caía por defecto en secundaria; en380/382 podía caer en total | Solicitado fallo cerrado con categorías reconocidas y test. No fue una discrepancia observada en la edición fijada, pero sí una ruta de interpretación silenciosa en el código. |
| Salud | `!=códigoNS` trataba un futuro código inesperado como dato especificado | Solicitada whitelist por variable y diccionario para cada edición, además de hash. El pin actual protege la edición descargada; no basta al aprobar una revisión con nuevo hash. |
| Salud | Denominador «total nacidos» no describía el conjunto de casos válidos | Se conserva total, elegible y desconocidos por variable. La conciliación exacta de componentes respalda el cálculo candidato; se necesita metodología de la edición2024, sin extrapolar regla a toda tasa. |
| Social | Cualquier ZIP2025/T3con nombre interno correcto recibía source_url constante | Solicitado pin de hash para procedencia exacta. El estado candidate/bloqueado evita publicación, pero una actualización óptima necesita integridad de edición desde adquisición. |
| Social | Edad−1e interpretación infantil sin corroboración | Mantener corte total separado; sensibilidades infantiles no aprobadas. La documentación consultada dice años cumplidos, pero no acredita ese código. |
| EPHU | Diferentes años/ponderadores/NSpueden generar estimaciones distintas | Agente social informó que2024tampoco reproduce la terna. Esto reduce una hipótesis, no prueba la causa ni autoriza reemplazo automático. |
| GIS | Geometrías inválidas o superpuestas | Gate de topología exigido solamente para presentación map/choropleth/proportional_symbols. Un fallo cartográfico no bloquea la tabla o barra técnicamente válida del mismo dato. |

Los cambios solicitados son revisión del código observado, no afirmación de que se haya reejecutado aquí el código final concurrente de otros agentes. Coordinación debe ejecutar la versión integrada y citar sus resultados finales.

## Semántica del gate

La función exige checks explícitos de integridad de fuente, esquema, granularidad, universo, período, geografía, cálculo y política de desconocidos. Un check ausente, desconocido o distinto de passed/not_applicable_documented no aprueba la vista. `not_applicable_documented` es una decisión de contrato que debe venir respaldada por evidencia, no un fallback automático.

La vista usa una lista cerrada de presentaciones y agregaciones permitidas. `AVG` no está permitido por defecto. Ratios con denominador elegible requieren el nombre exacto de la regla aprobada. EPHU exige dominio soportado y precisión estimada desde diseño o explícitamente no estimada/divulgada. La salida no fabrica errores estándar ni significación.

Para mapa se añade `geometry_topology=passed`; su falta o fallo impide incluso la vista previa del mapa. La misma información puede seguir siendo candidata para tabla/barra, siempre que supere los demás controles. La geometría usada por la versión integrada necesita su propio hash y aprobación en el sistema de despliegue, aunque este prototipo de gate registra el estado del check.

La autorización de publicación requiere además método de fuente, renderizado de Tableau, accesibilidad y una decisión approved para el scope exacto: hash, snapshot, view_id, indicator_id y reference_period. Una aprobación de otra edición no se hereda. No existe una aprobación humana en los registros de esta entrega.

**Límite de seguridad:** este es un validador estadístico/configuracional, no un servicio de autenticación. Verifica estructura y correspondencia del scope; no autentica personas ni firma decisiones. La integración debe permitir escribir decisiones aprobadas solo a responsables autorizados y conservar registro de auditoría. Nunca aceptar el objeto decision directamente desde parámetros públicos del navegador.

## Reproducibilidad

```sh
python create_evidence.py
python -m unittest discover -s /ruta/ladefe-team-round2/statistics -p 'test_publication_gate.py' -v
```

`create_evidence.py` usa rutas del entorno de auditoría para DB/XML y abre SQLite mode=ro; puede adaptarse esas rutas para otra instalación sin modificar datos. La prueba de20filas consume el JSON de evidencia versionado y por eso no requiere acceso a la base completa.

## Decisión final de esta revisión

El contrato temporal de salud se puede **normalizar como propuesta trazable de comparación2010/2022**, sin publicar ni sustituir raw_year. El de comedores **permanece indeterminado**. El doble redondeo educativo es una explicación técnica separada, no un error resuelto por tolerancia. Salud necesita dominio/diccionario y denominador elegible por medida; EPHU necesita universo y no respuesta explícitos. Publicar por vista es viable y está modelado como gate ejecutable; aún no hay vistas autorizadas para producción.

## Actualización cruzada de salud recibida al cierre

El agente de salud comunicó nueva evidencia primaria de la edición2024: anuario DEIS `serie_5_nro_68_anuario_vitales_2024_v2.pdf`, Cuadro6página46, con nota explícita sobre peso especificado. Esto permite elevar el respaldo documental de la regla de bajo peso; la aprobación temática humana sigue pendiente. Para gestación, Cuadro7página47 aporta conteos y no especificados, pero no una nota inequívoca del denominador porcentual: conservar la distinción entre coincidencia empírica y definición acreditada.

El mismo agente detectó `SEXO=3` en seis nacimientos y diez defunciones, aunque los diccionarios consultados solo etiquetan1/2/9. Decisión estadística: preservar el código y sus conteos; no inventar etiqueta ni eliminar esos eventos de los totales. Bloquear la vista por sexo o presentar un estado expresamente no homologado pendiente de aprobación, sin bloquear automáticamente las vistas totales cuya población siga siendo completa. La decisión puede resolverse por dimensión, no solo por indicador completo.

Se informó además una conciliación candidata de razón de mortalidad materna anual2024con183defuncionesM sobre413.135nacimientos por10.000, distinta de medidas trianuales. CódigosTtardía ySsecuela se conservan separados; no cambiar a ese cálculo un indicador trianual sin contrato distinto. Los resultados finales, hashes, páginas y pruebas del agente de salud deben ser la referencia al integrar estas conclusiones; esta subentrega no repitió esos cálculos adicionales.

Fuente documental comunicada por el agente: https://www.argentina.gob.ar/sites/default/files/serie_5_nro_68_anuario_vitales_2024_v2.pdf
