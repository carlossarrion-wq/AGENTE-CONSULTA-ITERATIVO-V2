# ESPECIFICACIÓN DE ARQUITECTURA - AGENTE DE CONSULTA ITERATIVO V2.0

**Proyecto**: Agente de Consulta Iterativo V2.0  
**Cliente**: Naturgy - Plataforma FactorIA  
**Versión**: 2.0  
**Fecha**: 23 de Diciembre de 2025  
**Estado**: Documento de Arquitectura Base

---

## 📋 TABLA DE CONTENIDOS

1. [Introducción y Alcance](#1-introducción-y-alcance)
2. [Arquitectura General](#2-arquitectura-general)
3. [Componentes Principales](#3-componentes-principales)
4. [Seguridad y Autenticación](#4-seguridad-y-autenticación)
5. [Gestión de Datos](#5-gestión-de-datos)
6. [Herramientas del Agente](#6-herramientas-del-agente)
7. [Interfaz de Usuario](#7-interfaz-de-usuario)
8. [Sistema Multi-Aplicación](#8-sistema-multi-aplicación)

---

## 1. INTRODUCCIÓN Y ALCANCE

### 1.1 Visión General

El Agente de Consulta Iterativo V2.0 representa una evolución arquitectónica del sistema actual, diseñado para proporcionar capacidades avanzadas de búsqueda y consulta sobre bases de conocimiento corporativas mediante lenguaje natural.

### 1.2 Objetivos Principales

- Modernizar la arquitectura mediante **Strands + Bedrock Agent Core**
- Implementar herramientas como **servicios MCP independientes**
- Fortalecer la seguridad con **IAM + JWT tokens**
- Optimizar el acceso a información con **8 herramientas especializadas**
- Mantener capacidad **multi-aplicación**
- Mejorar la **trazabilidad** con RDS PostgreSQL

### 1.3 Alcance

#### ✅ Dentro del Alcance
- Agente conversacional con Strands + Bedrock Agent Core
- 8 herramientas de búsqueda (servicios MCP)
- Interfaz web con chat y gestión de documentos
- Autenticación IAM + JWT
- Multi-aplicación (Darwin, SAP, MuleSoft, etc.)
- Trazabilidad en RDS PostgreSQL
- Streaming y prompt caching

#### ❌ Fuera del Alcance
- Pipeline de ingesta (desarrollo separado)
- Versionado de documentos
- Procesamiento de documentos (chunking, embeddings)

### 1.4 Evolución V1 → V2

| Aspecto | V1 | V2 |
|---------|----|----|
| **Arquitectura** | Monolítico | Strands + Agent Core + MCP |
| **Herramientas** | 4-6 integradas | 8 servicios MCP |
| **Búsqueda** | Semántica, Léxica | + Híbrida, Estructura, Lista |
| **Autenticación** | Simple | IAM + JWT |
| **Trazabilidad** | Logs + JSON | RDS PostgreSQL |

---

## 2. ARQUITECTURA GENERAL

### 2.1 Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────┐
│              CAPA DE APLICACIONES                        │
│        (Darwin, SAP, MuleSoft, DeltaSmile...)           │
└─────────────────────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    ┌───────▼────────┐       ┌───────▼────────┐
    │ Autenticación  │       │  Autorización  │
    │   (IAM+JWT)    │       │   (Permisos)   │
    └───────┬────────┘       └───────┬────────┘
            │                         │
            └────────────┬────────────┘
                         │
                ┌────────▼─────────┐
                │     API GW       │
                │  (REST + WS)     │
                └────────┬─────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌────▼────┐
│ Chat Module  │  │  Doc Mgr    │  │  Trace  │
└───────┬──────┘  └──────┬──────┘  └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                ┌────────▼─────────┐
                │   AGENTE CORE    │
                │ (Strands+Bedrock)│
                └────────┬─────────┘
                         │
                ┌────────▼─────────┐
                │  MCP Protocol    │
                └────────┬─────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────┐              ┌──────────▼──────┐
│ Search MCP   │              │   Document MCP  │
│ Server       │              │     Server      │
└───────┬──────┘              └──────────┬──────┘
        │                                 │
        └────────────────┬────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼─────┐
│  OpenSearch  │  │     S3      │  │    RDS    │
│ (Búsquedas)  │  │ (Docs+Meta) │  │ (Traza)   │
└──────────────┘  └─────────────┘  └───────────┘
```

### 2.2 Principios Arquitectónicos

1. **Separación de Responsabilidades**: Cada componente tiene un propósito específico
2. **Escalabilidad Horizontal**: Servidores MCP independientes
3. **Seguridad por Capas**: IAM → JWT → Autorización granular
4. **Extensibilidad**: Nuevas herramientas sin modificar el core
5. **Trazabilidad Completa**: Registro de todas las interacciones

---

## 3. COMPONENTES PRINCIPALES

### 3.1 Agente Core (Strands + Bedrock Agent Core)

**Propósito**: Motor central del agente conversacional

**Responsabilidades**:
- Gestión de conversaciones y contexto
- Orquestación de herramientas MCP
- Streaming de respuestas
- Prompt caching
- Gestión dinámica de memoria

**Tecnologías Clave**:
- **Strands**: Framework de agentes AWS
- **Bedrock Agent Core**: Runtime de agentes
- **Application Profile**: Gestión de acceso a LLM
- **Modelo LLM**: Claude Haiku 4.5 (configurable)

**Características**:
- Streaming nativo
- Prompt caching para optimización
- Gestión automática de ventana de contexto
- Trazabilidad de costes por equipo

### 3.2 Servidores MCP

**Arquitectura**: Microservicios independientes

**Servidores**:

1. **Search MCP Server** (Puerto 3000)
   - Búsqueda léxica (BM25)
   - Búsqueda semántica (embeddings)
   - Búsqueda híbrida (combinada)
   - Búsqueda por patrones (regex)

2. **Document MCP Server** (Puerto 3001)
   - Acceso a secciones de documentos
   - Obtención de documentos completos
   - Consulta de estructuras
   - Listado de documentos

**Ventajas**:
- Escalabilidad independiente
- Versionado por servidor
- Fácil mantenimiento
- Reutilización en otros proyectos

### 3.3 Capa de Datos

#### OpenSearch
- **Propósito**: Búsquedas léxicas y semánticas
- **Índices**: `rag-documents-{app_name}`
- **Vectores**: 384 dimensiones (Titan Embed Text V1)
- **Algoritmos**: BM25 (léxico) + KNN (semántico)

#### Amazon S3
- **Propósito**: Almacenamiento de documentos y metadata
- **Buckets**: `rag-system-{app_name}-{region}`
- **Estructura**:
  - `documents/` - Originales
  - `markdowns/` - Procesados
  - `summaries/` - Resúmenes
  - `structures/` - Estructuras
  - `snapshot/` - Inventario

**Estructura Detallada S3**:
```
s3://rag-system-{app_name}-eu-west-1/
│
├── documents/                          # [1] Documentos originales (INMUTABLE)
│   └── {subfolder}/
│       └── {filename}.{ext}
│
├── markdowns/                          # [2] Documentos procesados (.md)
│   └── {subfolder}/
│       └── {filename}.{ext}.md
│
├── summaries/                          # [3] Resúmenes generados (JSON)
│   └── {subfolder}/
│       └── {filename}.{ext}_summary.md
│
├── structures/                         # [4] Estructuras de documentos (Markdown)
│   └── {subfolder}/
│       └── {filename}.{ext}_structure.md
│
└── snapshots/                          # [5] Inventarios y control de versiones
    └── latest_state.json               # Estado actual del bucket
```

#### RDS PostgreSQL
- **Propósito**: Trazabilidad de interacciones
- **Endpoint**: `rag-postgres-v2.czuimyk2qu10.eu-west-1.rds.amazonaws.com`
- **Motor**: PostgreSQL
- **Región**: eu-west-1

**Modelo de Datos Simplificado (6 Tablas)**:

El modelo V2.0 se centra exclusivamente en trazabilidad de interacciones, eliminando tablas innecesarias de V1.0:

**1. web_sessions** - Sesiones web activas
- `session_token` (PK): Token de sesión JWT
- `user_arn`: ARN de IAM del usuario
- `user_name`: Nombre del usuario
- `iam_group`: Grupo IAM
- `created_at`: Fecha de creación
- `expires_at`: Fecha de expiración
- `last_activity`: Última actividad
- `ip_address`: IP del cliente
- `user_agent`: Navegador/cliente

**2. user_sessions** - Contexto conversacional
- `session_id` (PK): ID de sesión conversacional
- `user_id`: ID del usuario
- `created_at`: Fecha de creación
- `last_activity`: Última actividad
- `conversation_summary`: Resumen de la conversación
- `topics` (JSONB): Temas tratados
- `entities` (JSONB): Entidades mencionadas
- `preferences` (JSONB): Preferencias del usuario

**3. web_queries** - Consultas y respuestas
- `id` (PK): ID autoincremental
- `user_arn`: ARN de IAM del usuario
- `session_token` (FK): Referencia a web_sessions
- `query_text`: Texto de la consulta
- `llm_response`: Respuesta del agente
- `app_name`: Aplicación consultada
- `created_at`: Timestamp de consulta
- `response_time_ms`: Tiempo de respuesta
- `tokens_input`: Tokens de entrada
- `tokens_output`: Tokens de salida
- `tokens_total`: Total de tokens
- `retrieved_docs_count`: Documentos recuperados
- `status`: Estado (completed, error, etc.)
- `confidence_score`: Score de confianza

**4. tool_executions** - Ejecuciones de herramientas MCP
- `id` (PK): ID autoincremental
- `query_id` (FK): Referencia a web_queries
- `tool_name`: Nombre de la herramienta
- `tool_input` (JSONB): Parámetros de entrada
- `tool_output` (JSONB): Resultado de ejecución
- `execution_time_ms`: Tiempo de ejecución
- `success`: Éxito/fallo
- `error_message`: Mensaje de error (si aplica)
- `iteration`: Número de iteración
- `executed_at`: Timestamp de ejecución

**5. retrieved_documents** - Documentos recuperados
- `id` (PK): ID autoincremental
- `query_id` (FK): Referencia a web_queries
- `document_title`: Título del documento
- `document_content_substr`: Substring del contenido (max 1000 chars)
- `source_file`: Archivo fuente
- `similarity_score`: Score de similitud
- `rank_position`: Posición en ranking
- `tool_name`: Herramienta que lo recuperó
- `chunk_index`: Índice del chunk
- `total_chunks`: Total de chunks del documento
- `retrieved_at`: Timestamp de recuperación

**6. user_feedback** - Feedback de usuarios sobre respuestas
- `id` (PK): ID autoincremental
- `query_id` (FK): Referencia a web_queries
- `user_arn`: ARN de IAM del usuario
- `feedback_type`: Tipo de feedback ('like', 'dislike')
- `feedback_comment`: Comentario opcional del usuario (texto libre)
- `created_at`: Timestamp del feedback
- `updated_at`: Timestamp de última actualización
- `app_name`: Aplicación donde se dio el feedback

**Filosofía del Modelo**:
- Autenticación gestionada por IAM (no usuarios en BD)
- Referencias mediante ARN de IAM
- Enfoque en trazabilidad de interacciones
- Separación clara con proceso de ingesta

---

## 4. SEGURIDAD Y AUTENTICACIÓN

### 4.1 Flujo de Autenticación

```
1. Usuario → Credenciales AWS → Lambda Authenticator
2. Validación con AWS STS
3. Consulta políticas IAM
4. Generación JWT Token (60 min)
5. Cliente usa JWT en todas las peticiones
6. Lambda Authorizer valida cada petición
7. Acceso permitido/denegado según permisos
```

### 4.2 Niveles de Autorización

**Nivel 1: Aplicación**
- Acceso a aplicaciones específicas (Darwin, SAP, etc.)
- Definido en políticas IAM

**Nivel 2: Módulo**
- Acceso a módulos dentro de aplicaciones
- Chat, Document Manager, etc.
- Acciones: read, write, delete

**Nivel 3: Recurso**
- Control granular sobre recursos específicos
- Documentos, conversaciones, etc.

### 4.3 JWT Token

**Contenido**:
- `user_arn`: Identificador IAM del usuario
- `account_id`: Cuenta AWS
- `apps`: Permisos por aplicación y módulo
- `groups`: Grupos IAM del usuario
- `exp`: Expiración (60 minutos por defecto, configurable)

---

## 5. GESTIÓN DE DATOS

### 5.1 Contrato con Proceso de Ingesta

**Responsabilidad del Proceso de Ingesta**:
- Procesar documentos originales
- Generar Markdowns
- Crear resúmenes
- Generar estructuras
- Vectorizar y subir a OpenSearch
- Mantener inventario actualizado

**Responsabilidad del Agente V2**:
- Leer datos de S3
- Consultar OpenSearch
- Presentar información al usuario
- NO modificar datos de ingesta

### 5.2 Estructura de Datos en S3

**Documentos Markdown** (`.md`)
- Documento completo en formato Markdown
- Optimizado para LLM

**Resúmenes** (`_summary.json`)
- Resumen ejecutivo
- Puntos clave
- Temas principales
- Información técnica relevante

**Estructuras** (`_structure.json`)
- Tabla de contenidos
- Mapeo secciones → chunks
- Metadata de navegación

**Inventario** (`latest_state.json`)
- Lista completa de documentos
- Estado de procesamiento
- Hash MD5/SHA256 de cada archivo (para verificar sincronización con versión vectorizada)
- Estadísticas
- Sincronización con OpenSearch

### 5.3 Información en OpenSearch

**Documento Indexado**:
- `chunk_id`: Identificador único
- `file_name`: Nombre del archivo
- `content`: Contenido del chunk
- `embedding_vector`: Vector de 384 dimensiones
- `chunk_index`: Posición en el documento
- `metadata`: Información adicional

---

## 6. HERRAMIENTAS DEL AGENTE

### 6.1 Lista de Herramientas (8 Total)

1. **tool_lexical_search**
   - Búsqueda por palabras exactas (BM25)
   - Origen: OpenSearch
   - Uso: Términos técnicos específicos

2. **tool_semantic_search**
   - Búsqueda conceptual (embeddings)
   - Origen: OpenSearch
   - Uso: Preguntas en lenguaje natural

3. **tool_hybrid_search** ⭐ NUEVA
   - Búsqueda combinada ponderada
   - Origen: OpenSearch
   - Uso: Mejor de ambos mundos

4. **tool_structure**
   - Obtiene estructura del documento
   - Origen: S3
   - Uso: Tabla de contenidos

5. **tool_regex_search**
   - Búsqueda por patrones
   - Origen: OpenSearch
   - Uso: Emails, códigos, patrones

6. **tool_file_section**
   - Obtener chunks específicos
   - Origen: OpenSearch
   - Uso: Secciones concretas

7. **tool_file_content**
   - Obtener documento completo
   - Origen: S3
   - Uso: Documento entero

8. **tool_get_document_list** ⭐ NUEVA
   - Listar documentos disponibles
   - Origen: S3
   - Uso: Exploración inicial

### 6.2 Contratos de Operaciones MCP

#### 6.2.1 tool_lexical_search

**Origen de Datos**: OpenSearch - Índice `rag-documents-{app_name}` (campo `content` con algoritmo BM25)

**Entrada**:
```xml
<tool_lexical_search>
  <query>términos de búsqueda</query>
  <top_k>10</top_k>
  <case_sensitive>false</case_sensitive>
</tool_lexical_search>
```

**Salida**:
```xml
<lexical_search_result>
  <query>términos de búsqueda</query>
  <total_found>10</total_found>
  <search_type>lexical</search_type>
  <results>
    <result>
      <chunk_id>doc_chunk_0001</chunk_id>
      <file_name>documento.docx</file_name>
      <content>Contenido truncado (~500 chars)...</content>
      <score>15.234</score>
      <highlights>
        <highlight>término1</highlight>
        <highlight>término2</highlight>
      </highlights>
      <chunk_index>5</chunk_index>
    </result>
  </results>
</lexical_search_result>
```

#### 6.2.2 tool_semantic_search

**Origen de Datos**: OpenSearch - Índice `rag-documents-{app_name}` (campo `embedding_vector` con búsqueda KNN)

**Entrada**:
```xml
<tool_semantic_search>
  <query>pregunta conceptual</query>
  <top_k>10</top_k>
  <min_score>0.0</min_score>
</tool_semantic_search>
```

**Salida**:
```xml
<semantic_search_result>
  <query>pregunta conceptual</query>
  <total_found>10</total_found>
  <search_type>semantic</search_type>
  <results>
    <result>
      <chunk_id>doc_chunk_0002</chunk_id>
      <file_name>especificaciones/documento.docx</file_name>
      <content>Contenido truncado (~500 chars)...</content>
      <similarity_score>0.87</similarity_score>
      <chunk_index>3</chunk_index>
    </result>
  </results>
</semantic_search_result>
```

#### 6.2.3 tool_hybrid_search

**Origen de Datos**: OpenSearch - Índice `rag-documents-{app_name}` (combinación de BM25 + KNN con scoring ponderado)

**Entrada**:
```xml
<tool_hybrid_search>
  <query>términos + conceptos</query>
  <semantic_weight>0.6</semantic_weight>
  <lexical_weight>0.4</lexical_weight>
  <top_k>10</top_k>
  <min_score>0.0</min_score>
</tool_hybrid_search>
```

**Salida**:
```xml
<hybrid_search_result>
  <query>términos + conceptos</query>
  <total_found>10</total_found>
  <search_type>hybrid</search_type>
  <weights>
    <semantic>0.6</semantic>
    <lexical>0.4</lexical>
  </weights>
  <results>
    <result>
      <chunk_id>doc_chunk_0003</chunk_id>
      <file_name>especificaciones/documento.docx</file_name>
      <content>Contenido truncado (~500 chars)...</content>
      <combined_score>0.82</combined_score>
      <semantic_score>0.85</semantic_score>
      <lexical_score>12.5</lexical_score>
      <chunk_index>7</chunk_index>
    </result>
  </results>
</hybrid_search_result>
```

#### 6.2.4 tool_structure

**Origen de Datos**: S3 - Carpeta `structures/` → Archivo `{subfolder}/{filename}.{ext}_structure.md`

**Entrada**:
```xml
<tool_structure>
  <document_name>especificaciones/documento.docx</document_name>
</tool_structure>
```

**Salida**:
```xml
<structure_result>
  <document_name>especificaciones/documento.docx</document_name>
  <total_chunks>45</total_chunks>
  <structure>
    <section>
      <title>1. Introducción</title>
      <chunks>0,1,2</chunks>
    </section>
    <section>
      <title>2. Arquitectura</title>
      <chunks>3,4,5,6</chunks>
      <subsection>
        <title>2.1 Componentes</title>
        <chunks>7,8</chunks>
      </subsection>
    </section>
  </structure>
</structure_result>
```

#### 6.2.5 tool_regex_search

**Origen de Datos**: OpenSearch - Índice `rag-documents-{app_name}` (búsqueda por expresiones regulares en campo `content`)

**Entrada**:
```xml
<tool_regex_search>
  <pattern>\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b</pattern>
  <case_sensitive>false</case_sensitive>
  <context_lines>2</context_lines>
</tool_regex_search>
```

**Salida**:
```xml
<regex_search_result>
  <pattern>\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b</pattern>
  <total_matches>5</total_matches>
  <results>
    <result>
      <chunk_id>doc_chunk_0001</chunk_id>
      <file_name>especificaciones/documento.docx</file_name>
      <content>Contenido truncado (~500 chars)...</content>
      <score>15.234</score>
      <highlights>
        <highlight>término1</highlight>
        <highlight>término2</highlight>
      </highlights>
      <chunk_index>5</chunk_index>
    </result>
    <result>
      <file_name>especificaciones/documento.docx</file_name>
      <chunk_id>doc_chunk_0010</chunk_id>
      <match>usuario@ejemplo.com</match>
      <context>
        <line>línea anterior</line>
        <line>línea con usuario@ejemplo.com</line>
        <line>línea siguiente</line>
      </context>
      <line_number>42</line_number>
    </result>
  </results>
</regex_search_result>
```

#### 6.2.6 tool_file_section

**Origen de Datos**: OpenSearch - Índice `rag-documents-{app_name}` (recupera chunks específicos por `chunk_index`)

**Entrada**:
```xml
<tool_file_section>
  <file_name>especificaciones/documento.docx</file_name>
  <chunk_start>5</chunk_start>
  <chunk_end>10</chunk_end>
  <include_metadata>true</include_metadata>
</tool_file_section>
```

**Salida**:
```xml
<file_section_result>
  <file_name>especificaciones/documento.docx</file_name>
  <chunk_range>
    <start>5</start>
    <end>10</end>
  </chunk_range>
  <chunks>
    <chunk>
      <chunk_id>doc_chunk_0005</chunk_id>
      <chunk_index>5</chunk_index>
      <content>Contenido completo del chunk sin truncar...</content>
      <metadata>
        <section_title>Sección 2.1</section_title>
        <char_start>12500</char_start>
        <char_end>15000</char_end>
      </metadata>
    </chunk>
  </chunks>
</file_section_result>
```

#### 6.2.7 tool_file_content

**Origen de Datos**: S3 - Carpeta `markdowns/` → Archivo `{subfolder}/{filename}.{ext}.md` (documento completo en formato Markdown)

**Entrada**:
```xml
<tool_file_content>
  <file_name>especificaciones/documento.docx</file_name>
  <include_structure>true</include_structure>
</tool_file_content>
```

**Salida (Documento pequeño)**:
```xml
<file_content_result>
  <file_name>especificaciones/documento.docx</file_name>
  <mode>full_content</mode>
  <size>25000</size>
  <content>Contenido completo del documento...</content>
  <structure>...</structure>
</file_content_result>
```

**Salida (Documento grande - Modo Progresivo)**:
```xml
<file_content_result>
  <file_name>especificaciones/documento.docx</file_name>
  <mode>progressive</mode>
  <size>150000</size>
  <total_chunks>45</total_chunks>
  <message>Documento grande. Use tool_file_section para secciones específicas.</message>
  <structure>...</structure>
  <recommendation>Analice la estructura y solicite chunks específicos</recommendation>
</file_content_result>
```

#### 6.2.8 tool_get_document_list

**Origen de Datos**: S3 - Carpeta `snapshots/` → Archivo `latest_state.json` (inventario completo de documentos)

**Entrada**:
```xml
<tool_get_document_list>
  <app_name>darwin</app_name>
  <file_name>analisis*.pdf</file_name>
  <sort_by>name</sort_by>
  <include_stats>true</include_stats>
</tool_get_document_list>
```

**Salida**:
```xml
<document_list_result>
  <app_name>darwin</app_name>
  <total_documents>25</total_documents>
  <filters_applied>
    <file_name>analisis*.pdf</file_name>
    <sort_by>name</sort_by>
  </filters_applied>
  <documents>
    <document>
      <filename>especificaciones/documento1.docx</filename>
      <subfolder>especificaciones</subfolder>
      <extension>.docx</extension>
      <size>1247921</size>
      <chunks_count>45</chunks_count>
      <status>COMPLETE</status>
      <has_md>true</has_md>
      <has_summary>true</has_summary>
      <has_structure>true</has_structure>
    </document>
  </documents>
  <statistics>
    <total_size>52479214</total_size>
    <avg_chunks>38</avg_chunks>
    <by_extension>
      <docx>15</docx>
      <pdf>10</pdf>
    </by_extension>
  </statistics>
</document_list_result>
```

### 6.3 Modo Progresivo

Para documentos grandes (>50K caracteres):
- Primera llamada: Devuelve estructura
- Usuario solicita secciones específicas
- Acceso incremental al contenido

---

## 7. INTERFAZ DE USUARIO

### 7.1 Módulos

**Chat Module**
- Interfaz conversacional
- Streaming de respuestas
- Markdown y syntax highlighting
- Upload de archivos e imágenes
- Export de conversaciones
- Copy to clipboard
- **Sistema de feedback** (like/dislike por respuesta con comentario opcional)
  - Almacenado en tabla `user_feedback` de RDS
  - Permite análisis de calidad de respuestas
  - Comentarios opcionales para feedback detallado

**Document Manager**
- Listado de documentos
- Búsqueda y filtrado
- Visualización de metadata
- Descarga de documentos
- Indicadores de estado

### 7.2 Tecnologías Frontend

- **Framework**: React / Vue.js
- **Comunicación**: REST API + WebSocket
- **Estado**: Redux
- **Renderizado**: Markdown + Syntax Highlighter

---

## 8. SISTEMA MULTI-APLICACIÓN

### 8.1 Aplicaciones Soportadas

- **Darwin**: Sistema de contratación
- **SAP**: Documentación SAP
- **MuleSoft**: Integraciones y APIs
- **DeltaSmile**: Sistema específico
- **BPO MNC**: Procesos de negocio
- **SAP LCorp**: SAP corporativo

### 8.2 Application Profiles

**Concepto**: Capa de abstracción para acceso a LLM

**Beneficios**:
- Trazabilidad de costes por equipo
- Gestión centralizada de configuración
- Auditoría completa
- Control de límites y alertas

**Estructura**:
- Profile ID
- Configuración del modelo
- Límites de uso
- Tags para tracking de costes

### 8.3 Configuración por Aplicación

Cada aplicación tiene:
- Configuración YAML específica
- System prompt personalizado
- Application Profile asociado
- Herramientas habilitadas
- Features específicas

### 8.4 System Prompts

Define para cada aplicación:
- Rol del agente
- Herramientas disponibles
- Sinónimos y acrónimos del dominio
- Contexto específico
- Guías de respuesta

---

## CONCLUSIÓN

Esta especificación de arquitectura establece las bases del Agente de Consulta Iterativo V2.0, definiendo:

✅ **Arquitectura moderna** basada en Strands + Bedrock Agent Core  
✅ **Servicios MCP independientes** para máxima extensibilidad  
✅ **Seguridad robusta** con IAM + JWT  
✅ **8 herramientas especializadas** para acceso a información  
✅ **Sistema multi-aplicación** con Application Profiles  
✅ **Trazabilidad completa** en RDS PostgreSQL  

El siguiente paso será desarrollar especificaciones técnicas detalladas para cada componente, incluyendo APIs, contratos de datos, y guías de implementación.

---

**Documento**: ESPECIFICACION_ARQUITECTURA_AGENTE_V2.md  
**Versión**: 2.0  
**Fecha**: 23 de Diciembre de 2025  
**Estado**: Arquitectura Base Aprobada
