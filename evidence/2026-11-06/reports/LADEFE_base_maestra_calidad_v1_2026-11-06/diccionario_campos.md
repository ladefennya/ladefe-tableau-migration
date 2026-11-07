# Diccionario de Datos y reglas del backend

Se conserva el nombre y el valor exacto de la fuente en source_json. Las descripciones siguientes son operativas, derivadas del esquema y las reglas XML; no sustituyen la ficha metodológica del organismo.

| Campo fuente | Uso y precaución |
|---|---|
| TEMA_ID | Identificador de tema dentro de la versión de origen. |
| TEMA_NOMBRE | Etiqueta de tema; cambios de texto se conservan. |
| TABLERO_ID | Identificador del tablero; se combina con workbook. |
| SECCION_ID | Identificador de sección editorial; se preserva para filtros. |
| SECCION_NOMBRE | Nombre de sección. |
| GRUPO_INDICADOR_ID | Grupo de indicador, resuelto por workbook y versión. |
| INDICADOR_ID | Indicador, resuelto por workbook y versión. No usar como clave global aislada. |
| TIPO_DE_DATO | MAPA, SERIE_TEMPORAL, APERTURA o DISTRIBUCION. |
| ID_DATO_SM | Identificador técnico original; se conserva, sin asumir unicidad global. |
| DATO_DE_SISTEMA | Marca administrativa original; no se interpreta null como false. |
| ANIO | Año declarado; futuro exige aclaración de origen. |
| MES | Período textual: puede representar mes, trimestre o semestre. No convertir todo a meses. |
| UNIDAD_GEOGRAFICA_CODIGO | Código textual, manteniendo ceros iniciales. |
| UNIDAD_GEOGRAFICA_NOMBRE | Nombre de jurisdicción o agregado; no sumar agregado y componentes. |
| SUB_UNIDAD_GEOGRAFICA | Subunidad territorial; forma parte de la granularidad. |
| APERTURA_DESCRIPCION | Descripción de apertura; no mezclar universos. |
| APERTURA_NIVEL_1 | Primera dimensión de desagregación. |
| MODALIDAD_APERTURA_NIVEL_1 | Categoría de la primera dimensión. |
| APERTURA_NIVEL_2 | Segunda dimensión de desagregación. |
| MODALIDAD_APERTURA_NIVEL_2 | Categoría de la segunda dimensión. |
| VALOR | Medida original. En MAPA puede ser numerador; en otras vistas puede venir calculada. |
| VALOR_AUXILIAR | Medida auxiliar original; solo se interpreta como denominador según la regla de vista y unidad. No se aplica una fórmula genérica a todos los datos. |

observation_key es SHA-256 de workbook y dimensiones completas (excluye ID técnico, marca de sistema y medidas); snapshot distingue versiones. Cambiar una etiqueta dimensional puede producir otra clave. source_json permite reconstruir todas las columnas con sus tipos y nulos originales.

value_display conserva VALOR en las vistas no MAPA. Para MAPA: CANTIDAD conserva VALOR; PORCENTAJE y TASA_X_CIEN multiplican VALOR/VALOR_AUXILIAR por 100; TASA_X_MIL por 1.000; TASA_X_CIENMIL por 100.000; TASA_X_MILLON por 1.000.000; RAZON_X_DIEZMIL por 10.000. Unidad desconocida o denominador nulo/cero produce no_calculable y un error. Para agrupar varias filas se requiere regla aprobada: la base no calcula promedios ni asociaciones implícitas.

Los nulos y ausencias no son ceros. Las categorías no se consideran automáticamente exhaustivas ni mutuamente excluyentes. Cantidades monetarias, índices o coberturas no se consideran automáticamente aditivas. Los códigos de unidad de la fuente se preservan incluso cuando el nombre indica un índice base 100; esa discrepancia se documenta, no se reescribe.
