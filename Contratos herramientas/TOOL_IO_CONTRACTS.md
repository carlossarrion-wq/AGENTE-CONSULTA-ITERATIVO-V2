# Contratos de Entrada/Salida de Herramientas RAG

**Versión**: 1.0  
**Fecha**: 22/12/2025  
**Propósito**: Documentar el formato XML de entrada y el formato de respuesta para cada herramienta del agente conversacional

---

## 📋 Índice

1. [tool_lexical_search](#1-tool_lexical_search)
2. [tool_semantic_search](#2-tool_semantic_search)
3. [tool_structure_search](#3-tool_structure_search)
4. [tool_regex_search](#4-tool_regex_search)
5. [tool_file_section](#5-tool_file_section)
6. [tool_file_content](#6-tool_file_content)

---

## 1. tool_lexical_search

### 📥 Formato de Entrada (XML)

**Formato XML que escribe el LLM**:

```xml
<tool_lexical_search>
<query>términos de búsqueda</query>
<top_k>5</top_k>
</tool_lexical_search>
```

**Parámetros**:
- `query` (requerido): Términos de búsqueda exactos
- `top_k` (opcional): Número de resultados (default: 5, máximo: 10)

**Ejemplos**:

```xml
<!-- Búsqueda simple -->
<tool_lexical_search>
<query>MuleSoft APIKit</query>
</tool_lexical_search>

<!-- Con límite de resultados -->
<tool_lexical_search>
<query>Salesforce integración</query>
<top_k>10</top_k>
</tool_lexical_search>
```

### 📤 Formato de Salida

#### Formato Estructurado (SearchResult - Interno)

**Estructura de datos Python/JSON que devuelve la herramienta**:

```json
{
  "query": "MuleSoft APIKit",
  "expanded_query": "(MuleSoft OR plataforma) AND (APIKit OR framework)",
  "total_found": 3,
  "results": [
    {
      "chunk_id": "FD-Mulesoft_Funcional_chunk_0005",
      "score": 8.5,
      "source_file": "FD-Mulesoft_Funcional.docx",
      "content": "MuleSoft APIKit es un framework que permite construir APIs REST...",
      "highlights": [
        "<em>MuleSoft</em> <em>APIKit</em> es un framework..."
      ],
      "metadata": {
        "chunk_type": "content",
        "section_title": "Herramientas de Desarrollo",
        "keywords": ["mulesoft", "apikit", "rest", "framework"],
        "has_tables": false,
        "has_images": false
      }
    },
    {
      "chunk_id": "FD-Mulesoft_Funcional_chunk_0012",
      "score": 7.2,
      "source_file": "FD-Mulesoft_Funcional.docx",
      "content": "Para implementar una API con APIKit, primero debe crear...",
      "highlights": [],
      "metadata": {
        "chunk_type": "content",
        "section_title": "Implementación de APIs",
        "keywords": ["api", "apikit", "implementación"]
      }
    }
  ],
  "execution_time_ms": 245.3,
  "search_params": {
    "operator": "OR",
    "top_k": 5,
    "filters_applied": {},
    "synonyms_used": ["plataforma", "framework"]
  },
  "search_type": "lexical_search"
}
```

#### Formato de Texto (LLM Response - Lo que ve el agente)

**Estructura de respuesta que recibe el LLM**:

```
[RESULTADOS DE TU BÚSQUEDA]

RECORDATORIO - Pregunta original del usuario: "pregunta del usuario"

INSTRUCCIONES:
1. Analiza estos resultados cuidadosamente
2. Presenta una respuesta natural y útil al usuario
3. Cita las fuentes mencionando los documentos
4. Si la información no es suficiente, dilo claramente

📊 Total de búsquedas ejecutadas: 1
   Exitosas: 1
   Fallidas: 0

🔍 Búsqueda léxica: 'MuleSoft APIKit'
   Resultados encontrados: 3
   Query expandida: '(MuleSoft OR plataforma) AND (APIKit OR framework)'

[Resultado 1]
Documento: FD-Mulesoft_Funcional.docx
ID: FD-Mulesoft_Funcional_chunk_0005
Score: 8.5
Contenido:
MuleSoft APIKit es un framework que permite construir APIs REST de manera rápida y eficiente. Proporciona scaffolding automático basado en especificaciones RAML o OAS, validación de requests, y generación de flujos...

[Resultado 2]
Documento: FD-Mulesoft_Funcional.docx
ID: FD-Mulesoft_Funcional_chunk_0012
Score: 7.2
Contenido:
Para implementar una API con APIKit, primero debe crear una especificación RAML que defina los endpoints, métodos HTTP, y esquemas de datos. Luego, APIKit genera automáticamente los flujos principales y...

[Resultado 3]
Documento: Guia_Implementacion_MuleSoft.md
ID: Guia_Implementacion_MuleSoft_chunk_0003
Score: 6.8
Contenido:
El APIKit Router es el componente central que procesa las peticiones HTTP entrantes y las enruta al flujo correspondiente basándose en la especificación RAML. Soporta validaciones automáticas de...
```

**Elementos de la respuesta**:
- **Header**: Instrucciones y contexto
- **Metadata**: Total de búsquedas, éxito/fallo
- **Query info**: Query original y expandida
- **Resultados**: Lista de chunks con:
  - Documento origen
  - ID del chunk
  - Score de relevancia (BM25)
  - Contenido (truncado a ~500 caracteres)

---

## 2. tool_semantic_search

### 📥 Formato de Entrada (XML)

```xml
<tool_semantic_search>
<query>pregunta conceptual o descripción</query>
<top_k>10</top_k>
<min_score>0.0</min_score>
</tool_semantic_search>
```

**Parámetros**:
- `query` (requerido): Pregunta en lenguaje natural o concepto
- `top_k` (opcional): Número de resultados (default: 10, máximo: 50)
- `min_score` (opcional): Score mínimo 0.0-1.0 (default: 0.0)

**Ejemplos**:

```xml
<!-- Pregunta conceptual -->
<tool_semantic_search>
<query>¿Cómo funciona el proceso de autenticación?</query>
<top_k>5</top_k>
</tool_semantic_search>

<!-- Búsqueda por concepto -->
<tool_semantic_search>
<query>arquitectura de integración de sistemas</query>
<top_k>10</top_k>
<min_score>0.0</min_score>
</tool_semantic_search>
```

### 📤 Formato de Salida

#### Formato Estructurado (SearchResult - Interno)

```json
{
  "query": "¿Cómo funciona el proceso de autenticación?",
  "expanded_query": null,
  "total_found": 5,
  "results": [
    {
      "chunk_id": "FD-Mulesoft_Funcional_chunk_0008",
      "score": 0.8234,
      "source_file": "FD-Mulesoft_Funcional.docx",
      "content": "El proceso de autenticación se basa en OAuth 2.0 con tokens JWT...",
      "highlights": [],
      "metadata": {
        "chunk_type": "content",
        "section_title": "Seguridad y Autenticación",
        "keywords": ["oauth", "jwt", "autenticación", "seguridad"]
      }
    }
  ],
  "execution_time_ms": 387.5,
  "search_params": {
    "top_k": 5,
    "min_score": 0.0,
    "embedding_model": "amazon.titan-embed-image-v1"
  },
  "search_type": "semantic_search"
}
```

#### Formato de Texto (LLM Response)

```
[RESULTADOS DE TU BÚSQUEDA]

RECORDATORIO - Pregunta original del usuario: "¿Cómo funciona el proceso de autenticación?"

INSTRUCCIONES:
1. Analiza estos resultados cuidadosamente
2. Presenta una respuesta natural y útil al usuario
3. Cita las fuentes mencionando los documentos
4. Si la información no es suficiente, dilo claramente

📊 Total de búsquedas ejecutadas: 1
   Exitosas: 1
   Fallidas: 0

🧠 Búsqueda semántica: '¿Cómo funciona el proceso de autenticación?'
   Resultados encontrados: 5
   Modelo: amazon.titan-embed-image-v1

[Resultado 1]
Documento: FD-Mulesoft_Funcional.docx
ID: FD-Mulesoft_Funcional_chunk_0008
Similitud: 0.8234
Contenido:
El proceso de autenticación se basa en OAuth 2.0 con tokens JWT. Cuando un usuario accede al sistema, sus credenciales se validan contra el servicio de identidad corporativo. Si la validación es exitosa...

[Resultado 2]
Documento: Guia_Seguridad_APIs.md
ID: Guia_Seguridad_APIs_chunk_0015
Similitud: 0.7891
Contenido:
La autenticación de usuarios sigue un flujo de dos pasos: primero, verificación de credenciales mediante LDAP o Active Directory; segundo, generación de un token de sesión con tiempo de expiración...

[...]
```

**Diferencias con lexical_search**:
- Score: **Similitud** (0.0-1.0) en lugar de BM25
- Query: No se expande con sinónimos
- Modelo: Indica qué modelo de embeddings se usó

---

## 3. tool_structure_search

### 📥 Formato de Entrada (XML)

```xml
<tool_structure_search>
<document_name>nombre_documento.ext</document_name>
<chunk_type>table</chunk_type>
<keywords>keyword1,keyword2</keywords>
<position>first_5</position>
<top_k>10</top_k>
</tool_structure_search>
```

**Parámetros**:
- `document_name` (requerido): Nombre exacto con extensión
- `chunk_type` (opcional): "section_header", "table", "content"
- `keywords` (opcional): Keywords separadas por comas
- `position` (opcional): "first_5", "last_3", "all"
- `top_k` (opcional): Máximo resultados (default: 10, máximo: 50)

**Ejemplos**:

```xml
<!-- Buscar tablas en documento -->
<tool_structure_search>
<document_name>FD-Mulesoft_Funcional.docx</document_name>
<chunk_type>table</chunk_type>
</tool_structure_search>

<!-- Buscar secciones con keywords -->
<tool_structure_search>
<document_name>DOCUMENTACION_SERVICIO_FIRMAS.md</document_name>
<keywords>autenticación,token,oauth</keywords>
<position>all</position>
</tool_structure_search>

<!-- Buscar encabezados -->
<tool_structure_search>
<document_name>FD-Mulesoft_Funcional.docx</document_name>
<chunk_type>section_header</chunk_type>
<position>first_5</position>
</tool_structure_search>
```

### 📤 Formato de Salida (Texto)

```
[RESULTADOS DE TU BÚSQUEDA]

RECORDATORIO - Pregunta original del usuario: "¿Qué tablas hay en el documento funcional?"

INSTRUCCIONES:
1. Analiza estos resultados cuidadosamente
2. Presenta una respuesta natural y útil al usuario
3. Cita las fuentes mencionando los documentos
4. Si la información no es suficiente, dilo claramente

📊 Total de búsquedas ejecutadas: 1
   Exitosas: 1
   Fallidas: 0

🏗️  Búsqueda estructural: documento 'FD-Mulesoft_Funcional.docx'
   Resultados encontrados: 4
   Filtros: chunk_type=table

[Resultado 1]
Documento: FD-Mulesoft_Funcional.docx
ID: FD-Mulesoft_Funcional_chunk_0023
Tipo: table
Contenido:
| Módulo | Responsabilidad | Tecnología |
|--------|-----------------|------------|
| API Gateway | Gestión de APIs | MuleSoft APIKit |
| Service Layer | Lógica de negocio | Java/DataWeave |
| Integration Layer | Conectores externos | MuleSoft Connectors |

[Resultado 2]
Documento: FD-Mulesoft_Funcional.docx
ID: FD-Mulesoft_Funcional_chunk_0045
Tipo: table
Contenido:
Tabla de configuración de endpoints:
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| /api/users | GET | Listar usuarios |
| /api/users/{id} | GET | Obtener usuario específico |
[...]
```

**Notas especiales**:
- Si estructura no disponible, hace fallback automático a `lexical_search`
- El fallback es transparente para el LLM (no se menciona el error)

---

## 4. tool_regex_search

### 📥 Formato de Entrada (XML)

**Opción 1: Patrón predefinido**
```xml
<tool_regex_search>
<predefined>email</predefined>
<context_lines>2</context_lines>
</tool_regex_search>
```

**Opción 2: Patrón personalizado**
```xml
<tool_regex_search>
<pattern>\bAPI[-_]?KEY\b</pattern>
<case_sensitive>true</case_sensitive>
<context_lines>1</context_lines>
<max_matches_per_file>50</max_matches_per_file>
</tool_regex_search>
```

**Parámetros**:
- `predefined` (opcional): Nombre de patrón predefinido (ej: "email", "url", "version")
- `pattern` (opcional): Expresión regular personalizada
- `case_sensitive` (opcional): true/false (default: false)
- `context_lines` (opcional): Líneas de contexto (default: 2, max: 20)
- `max_matches_per_file` (opcional): Límite por archivo (default: 50, max: 100)

**IMPORTANTE**: Usar `predefined` O `pattern`, no ambos.

**Ejemplos**:

```xml
<!-- Buscar emails -->
<tool_regex_search>
<predefined>email</predefined>
</tool_regex_search>

<!-- Buscar versiones de software -->
<tool_regex_search>
<predefined>version</predefined>
<context_lines>3</context_lines>
</tool_regex_search>

<!-- Patrón personalizado -->
<tool_regex_search>
<pattern>REF-\d{4}-[A-Z]{3}</pattern>
<case_sensitive>true</case_sensitive>
</tool_regex_search>
```

### 📤 Formato de Salida (Texto)

```
[RESULTADOS DE TU BÚSQUEDA]

RECORDATORIO - Pregunta original del usuario: "¿Qué emails aparecen en la documentación?"

INSTRUCCIONES:
1. Analiza estos resultados cuidadosamente
2. Presenta una respuesta natural y útil al usuario
3. Cita las fuentes mencionando los documentos
4. Si la información no es suficiente, dilo claramente

📊 Total de búsquedas ejecutadas: 1
   Exitosas: 1
   Fallidas: 0

🔎 Búsqueda por regex: patrón 'email'
   Total de coincidencias: 8 en 3 archivos

[Archivo: FD-Mulesoft_Funcional.docx]
Total de matches: 3

Match 1: soporte.mulesoft@company.com
Contexto:
Para contactar con el equipo de integración, envíe un correo a
soporte.mulesoft@company.com con el asunto "Consulta MuleSoft" y 
una descripción detallada del problema.

Match 2: admin@mulesoft-prod.com
Contexto:
El administrador del entorno de producción es contactable en
admin@mulesoft-prod.com. Este correo debe usarse solo para
incidencias críticas que requieran atención inmediata.

[Archivo: Guia_Contactos.md]
Total de matches: 5

Match 1: desarrollo@company.com
Contexto:
Equipo de desarrollo: desarrollo@company.com
Horario: Lunes a Viernes 9:00-18:00
[...]
```

---

## 5. tool_file_section

### 📥 Formato de Entrada (XML)

```xml
<tool_file_section>
<file_name>nombre_archivo.ext</file_name>
<chunk_start>5</chunk_start>
<chunk_end>10</chunk_end>
<include_metadata>true</include_metadata>
</tool_file_section>
```

**Parámetros**:
- `file_name` (requerido): Nombre con o sin extensión
- `chunk_start` (requerido): Índice inicial (1-based, inclusive)
- `chunk_end` (requerido): Índice final (1-based, inclusive)
- `include_metadata` (opcional): true/false (default: false)

**Límites**:
- Mínimo chunk_start: 1
- Máximo rango: 100 chunks por solicitud

**Ejemplos**:

```xml
<!-- Obtener sección específica -->
<tool_file_section>
<file_name>FD-Mulesoft_Funcional.docx</file_name>
<chunk_start>5</chunk_start>
<chunk_end>8</chunk_end>
</tool_file_section>

<!-- Con metadata de estructura -->
<tool_file_section>
<file_name>DOCUMENTACION_FLUJO_FACTURAS_SAP.md.md</file_name>
<chunk_start>1</chunk_start>
<chunk_end>3</chunk_end>
<include_metadata>true</include_metadata>
</tool_file_section>
```

### 📤 Formato de Salida (Texto)

**Sin metadata**:
```
[RESULTADOS DE TU BÚSQUEDA]

RECORDATORIO - Pregunta original del usuario: "Dame el contenido de los chunks 5-8"

INSTRUCCIONES:
1. Analiza estos resultados cuidadosamente
2. Presenta una respuesta natural y útil al usuario
3. Cita las fuentes mencionando los documentos

📊 Sección de archivo obtenida
   Archivo: FD-Mulesoft_Funcional.docx
   Chunks solicitados: 5-8
   Chunks encontrados: 4

[Chunk 5]
ID: FD-Mulesoft_Funcional_chunk_0005
Índice: 5

## 3.1 Arquitectura de Integración

La arquitectura de integración de MuleSoft se basa en una topología de hub-and-spoke
donde el API Gateway actúa como punto central de entrada. Cada sistema externo se
conecta mediante conectores específicos que abstraen la complejidad de las APIs
subyacentes.

[Contenido completo del chunk sin truncar]

[Chunk 6]
ID: FD-Mulesoft_Funcional_chunk_0006
Índice: 6

### 3.1.1 Capa de API Gateway

El API Gateway es responsable de:
- Autenticación y autorización de peticiones
- Rate limiting y throttling
- Transformación de protocolos (REST, SOAP, etc.)
- Enrutamiento dinámico basado en reglas de negocio

[Contenido completo del chunk sin truncar]

[...]
```

**Con metadata (include_metadata=true)**:
```
[RESULTADOS DE TU BÚSQUEDA]

[...]

[Chunk 5]
ID: FD-Mulesoft_Funcional_chunk_0005
Índice: 5

📋 Metadata del chunk:
   Descripción: Arquitectura de integración basada en hub-and-spoke con API Gateway central
   Keywords: mulesoft, gateway, integración, hub, spoke

## 3.1 Arquitectura de Integración

[Contenido completo...]

[Chunk 6]
ID: FD-Mulesoft_Funcional_chunk_0006
Índice: 6

📋 Metadata del chunk:
   Descripción: Responsabilidades del API Gateway incluyendo autenticación, rate limiting y enrutamiento
   Keywords: gateway, autenticación, throttling, enrutamiento

[Contenido completo...]
```

---

## 6. tool_file_content

### 📥 Formato de Entrada (XML)

```xml
<tool_file_content>
<file_name>nombre_archivo.ext</file_name>
<include_structure>true</include_structure>
</tool_file_content>
```

**Parámetros**:
- `file_name` (requerido): Nombre con o sin extensión
- `include_structure` (opcional): true/false (default: true)

**Ejemplos**:

```xml
<!-- Obtener documento completo con estructura -->
<tool_file_content>
<file_name>DOCUMENTACION_FLUJO_FACTURAS_SAP.md.md</file_name>
</tool_file_content>

<!-- Sin estructura (más rápido) -->
<tool_file_content>
<file_name>FD-Mulesoft_Funcional.md</file_name>
<include_structure>false</include_structure>
</tool_file_content>
```

### 📤 Formato de Salida (Texto)

**Con estructura (include_structure=true)**:
```
[RESULTADOS DE TU BÚSQUEDA]

RECORDATORIO - Pregunta original del usuario: "¿Qué contiene el documento de facturas?"

INSTRUCCIONES:
1. Analiza estos resultados cuidadosamente
2. Presenta una respuesta natural y útil al usuario
3. Usa la estructura para identificar secciones relevantes

📄 Contenido completo del archivo
   Archivo: DOCUMENTACION_FLUJO_FACTURAS_SAP.md.md
   Tamaño: 12,519 caracteres
   Total chunks: 6
   Estructura disponible: Sí

═══════════════════════════════════════════════════════════════
CONTENIDO COMPLETO
═══════════════════════════════════════════════════════════════

# DOCUMENTACION_FLUJO_FACTURAS_SAP

## Introducción

Este documento describe el flujo batch `sftp-facturas-Real-Sap-Flow` que 
automatiza el procesamiento de facturas cada 30 segundos...

[Contenido completo sin truncar - continúa hasta el final del documento]

═══════════════════════════════════════════════════════════════
ESTRUCTURA DEL DOCUMENTO (6 chunks)
═══════════════════════════════════════════════════════════════

📋 Chunk 0: DOCUMENTACION_FLUJO_FACTURAS_SAP_md_chunk_0000
   Descripción: Documentación del flujo batch sftp-facturas-Real-Sap-Flow que 
   automatiza procesamiento de facturas cada 30 segundos. Describe arquitectura 
   completa: descarga de ZIPs desde S3, descompresión, procesamiento paralelo...
   Keywords: sap, archivos, fol

📋 Chunk 1: DOCUMENTACION_FLUJO_FACTURAS_SAP_md_chunk_0001
   Descripción: Describe el flujo integral de procesamiento de facturas desde S3: 
   descarga y extracción de ZIPs con concurrencia controlada, validación de XMLs...
   Keywords: sap, omega, cliente

📋 Chunk 2: DOCUMENTACION_FLUJO_FACTURAS_SAP_md_chunk_0002
   Descripción: Define tres modalidades de envío de facturas (INT, LET, FAE) con 
   sus respectivas condiciones y acciones en Marketing Cloud...
   Keywords: archivos, sap, contrato

📋 Chunk 3: DOCUMENTACION_FLUJO_FACTURAS_SAP_md_chunk_0003
   Descripción: Define estrategia integral de manejo de errores, gestión de archivos 
   y configuración de propiedades del sistema...
   Keywords: sap, archivos, sap

📋 Chunk 4: DOCUMENTACION_FLUJO_FACTURAS_SAP_md_chunk_0004
   Descripción: Define la arquitectura de integraciones externas del sistema de 
   procesamiento de facturas, incluyendo conectores a S3, DynamoDB...
   Keywords: archivos, sap, cliente

📋 Chunk 5: DOCUMENTACION_FLUJO_FACTURAS_SAP_md_chunk_0005
   Descripción: Define casos de uso operacionales del sistema de facturación: 
   procesamiento estándar de ZIPs, generación de facturas electrónicas...
   Keywords: cliente, archivos, sap

═══════════════════════════════════════════════════════════════
```

**Sin estructura (include_structure=false)**:
```
[RESULTADOS DE TU BÚSQUEDA]

RECORDATORIO - Pregunta original del usuario: "Muéstrame el documento completo"

📄 Contenido completo del archivo
   Archivo: DOCUMENTACION_FLUJO_FACTURAS_SAP.md.md
   Tamaño: 12,519 caracteres
   Estructura disponible: No

═══════════════════════════════════════════════════════════════
CONTENIDO COMPLETO
═══════════════════════════════════════════════════════════════

[Contenido completo del documento sin estructura adicional]

═══════════════════════════════════════════════════════════════
```

---

## 🔄 Flujo General de Interacción

### 1. LLM Escribe XML

El LLM analiza la consulta del usuario y genera XML:

```xml
<tool_lexical_search>
<query>MuleSoft integración</query>
<top_k>5</top_k>
</tool_lexical_search>
```

### 2. Sistema Parsea y Ejecuta

`tool_executor.py`:
1. Extrae parámetros del XML con regex
2. Convierte tipos (strings → int, etc.)
3. Llama a la herramienta: `lexical_search.search(**params)`
4. Obtiene `SearchResult`

### 3. Sistema Formatea Respuesta

`conversational_agent.py`:
1. Convierte `SearchResult` a texto formateado
2. Trunca contenidos a ~500 caracteres
3. Añade instrucciones y contexto
4. Devuelve al LLM

### 4. LLM Analiza y Responde

El LLM:
1. Lee los resultados
2. Analiza relevancia
3. Formula respuesta al usuario
4. Cita fuentes

---

## 📊 Comparativa de Herramientas

| Herramienta | Tipo de Búsqueda | Score | Contenido | Metadata |
|-------------|------------------|-------|-----------|----------|
| lexical_search | Palabras exactas | BM25 (0-∞) | Truncado 500 chars | Básica |
| semantic_search | Conceptual | Similitud (0-1) | Truncado 500 chars | Básica |
| structure_search | Estructural | N/A | Truncado 500 chars | Tipo chunk |
| regex_search | Patrones | N/A | Con contexto | Matches |
| file_section | Chunks específicos | N/A | **Completo** | Opcional |
| file_content | Documento completo | N/A | **Completo** | Estructura |

---

## ⚠️ Notas Importantes

### Truncado de Contenido

- **Búsquedas** (lexical, semantic, structure, regex): Contenido truncado a ~500 caracteres
- **Acceso directo** (file_section, file_content): Contenido **completo sin truncar**

### Metadata Enriquecida

Solo disponible con `include_metadata=true`:
- `file_section`: Descripciones y keywords por chunk
- `file_content`: Estructura completa con todos los chunks

### Fallbacks Automáticos

- `structure_search` → `lexical_search` si estructura no disponible
- El fallback es **transparente** para el LLM

### Límites

- `lexical_search`: max 10 resultados
- `semantic_search`: max 50 resultados
- `structure_search`: max 50 resultados
- `regex_search`: max 100 matches por archivo
- `file_section`: max 100 chunks por solicitud

---

## 🎯 Casos de Uso Recomendados

### Exploración General → `file_content`
```xml
<tool_file_content>
<file_name>documento.md</file_name>
</tool_file_content>
```

### Búsqueda Conceptual → `semantic_search`
```xml
<tool_semantic_search>
<query>¿Cómo funciona la autenticación?</query>
</tool_semantic_search>
```

### Término Técnico Exacto → `lexical_search`
```xml
<tool_lexical_search>
<query>MuleSoft APIKit v4.5</query>
</tool_lexical_search>
```

### Explorar Estructura → `structure_search`
```xml
<tool_structure_search>
<document_name>documento.md</document_name>
<chunk_type>table</chunk_type>
</tool_structure_search>
```

### Detalle de Sección → `file_section`
```xml
<tool_file_section>
<file_name>documento.md</file_name>
<chunk_start>5</chunk_start>
<chunk_end>10</chunk_end>
</tool_file_section>
```

### Patrones Estructurados → `regex_search`
```xml
<tool_regex_search>
<predefined>email</predefined>
</tool_regex_search>
```

---

**Autor**: Sistema RAG  
**Versión**: 1.0  
**Última actualización**: 22/12/2025
