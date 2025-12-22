# CONCEPTUALIZACIÓN AGENTE DE CONSULTA ITERATIVO V2.0

## 📋 RESUMEN EJECUTIVO

Este documento define la arquitectura y características del **Agente de Consulta Iterativo V2.0**, una evolución significativa del sistema actual que incorpora:

- **Arquitectura moderna**: Migración a Strands + Bedrock Agent Core
- **Mejoras de ingesta**: Nuevos métodos de procesamiento más precisos
- **Herramientas MCP**: Extensibilidad mediante Model Context Protocol
- **Herramientas avanzadas**: 7 herramientas de búsqueda y recuperación
- **Funcionalidades UI mejoradas**: Subida de archivos, imágenes, exportación
- **Control de acceso IAM**: Modelo basado en roles y perfiles AWS

---

## 🎯 OBJETIVOS DEL PROYECTO

### Objetivos Principales

1. **Modernizar la arquitectura** hacia Strands + Bedrock Agent Core (estándar FactorIA de Naturgy)
2. **Mejorar la precisión** de ingesta y recuperación de información
3. **Aumentar la extensibilidad** mediante herramientas MCP
4. **Enriquecer la experiencia de usuario** con nuevas funcionalidades UI
5. **Fortalecer la seguridad** con control de acceso basado en IAM

### Objetivos Secundarios

- Mantener compatibilidad con bases de conocimiento existentes
- Reducir latencia en consultas mediante optimizaciones
- Facilitar la administración de documentos
- Mejorar la observabilidad y trazabilidad del sistema

---

## 🏗️ ARQUITECTURA V2.0

### Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENTE DE CONSULTA ITERATIVO V2.0                        │
│                     (Strands + Bedrock Agent Core)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        CAPA DE PRESENTACIÓN                          │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  • Interfaz Web (React/Next.js)                                      │  │
│  │  • Módulo Chat Conversacional                                        │  │
│  │  • Módulo Gestión Documentos                                         │  │
│  │  • Upload de Archivos e Imágenes                                     │  │
│  │  • Exportación de Conversaciones                                     │  │
│  │  • Copy to Clipboard                                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    ↕                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA DE ORQUESTACIÓN (STRANDS)                    │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  • Strands Agent Framework                                           │  │
│  │  • Bedrock Agent Core Runtime                                        │  │
│  │  • Session Management                                                │  │
│  │  • Conversation Context Manager                                      │  │
│  │  • Prompt Cache Manager                                              │  │
│  │  • Tool Orchestrator                                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    ↕                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA DE HERRAMIENTAS (MCP)                        │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  MCP Server 1: Búsqueda y Recuperación                              │  │
│  │  ├─ tool_semantic_search                                             │  │
│  │  ├─ tool_lexical_search                                              │  │
│  │  ├─ tool_hybrid_search                                               │  │
│  │  └─ tool_regex_search                                                │  │
│  │                                                                       │  │
│  │  MCP Server 2: Gestión de Documentos                                │  │
│  │  ├─ tool_get_document_structure                                      │  │
│  │  ├─ tool_list_documents                                              │  │
│  │  ├─ tool_get_full_document                                           │  │
│  │  └─ tool_get_document_section                                        │  │
│  │                                                                       │  │
│  │  MCP Server 3: Administración (futuro)                              │  │
│  │  ├─ tool_upload_document                                             │  │
│  │  ├─ tool_delete_document                                             │  │
│  │  └─ tool_reindex_document                                            │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    ↕                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA DE DATOS Y SERVICIOS                         │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  • OpenSearch (Índices Vectoriales + Léxicos)                       │  │
│  │  • S3 (Almacenamiento de Documentos)                                │  │
│  │  • Bedrock (LLM + Embeddings)                                        │  │
│  │  • DynamoDB (Metadatos y Sesiones)                                  │  │
│  │  • CloudWatch (Logs y Métricas)                                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    ↕                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA DE SEGURIDAD (IAM)                           │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  • AWS IAM Authentication                                            │  │
│  │  • Role-Based Access Control (RBAC)                                 │  │
│  │  • Access Key + Secret Management                                   │  │
│  │  • Resource-Level Permissions                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. Strands Agent Framework
- **Propósito**: Framework de orquestación de agentes de AWS
- **Responsabilidades**:
  - Gestión del ciclo de vida del agente
  - Coordinación de herramientas
  - Manejo de estado conversacional
  - Integración con Bedrock Agent Core

#### 2. Bedrock Agent Core
- **Propósito**: Runtime serverless para agentes
- **Características**:
  - Escalado automático
  - Gestión de memoria persistente
  - Observabilidad integrada
  - Ejecución segura de código

#### 3. MCP Servers
- **Propósito**: Servidores de herramientas extensibles
- **Ventajas**:
  - Desacoplamiento de herramientas
  - Fácil extensibilidad
  - Versionado independiente
  - Reutilización entre agentes

---

## 🔧 HERRAMIENTAS DEL AGENTE V2.0

### Herramientas de Búsqueda y Recuperación

#### 1. tool_semantic_search
**Descripción**: Búsqueda semántica usando embeddings vectoriales

**Parámetros**:
```json
{
  "query": "string (requerido)",
  "top_k": "integer (opcional, default: 10)",
  "min_score": "float (opcional, default: 0.5)",
  "file_types": "array<string> (opcional)",
  "filters": {
    "date_range": "object (opcional)",
    "metadata": "object (opcional)"
  }
}
```

**Mejoras V2**:
- Soporte para filtros avanzados
- Reranking con modelos especializados
- Explicabilidad de resultados (por qué se seleccionó cada resultado)

#### 2. tool_lexical_search
**Descripción**: Búsqueda léxica tradicional (BM25)

**Parámetros**:
```json
{
  "query": "string (requerido)",
  "fields": "array<string> (opcional)",
  "operator": "AND|OR (opcional)",
  "top_k": "integer (opcional)",
  "fuzzy": "boolean (opcional)",
  "boost_fields": "object (opcional)"
}
```

**Mejoras V2**:
- Boost configurable por campo
- Sinónimos y expansión de términos
- Highlighting mejorado

#### 3. tool_hybrid_search (NUEVO)
**Descripción**: Búsqueda híbrida combinando semántica + léxica

**Parámetros**:
```json
{
  "query": "string (requerido)",
  "semantic_weight": "float (opcional, default: 0.5)",
  "lexical_weight": "float (opcional, default: 0.5)",
  "top_k": "integer (opcional)",
  "rerank": "boolean (opcional, default: true)"
}
```

**Estrategia**:
- Ejecuta búsqueda semántica y léxica en paralelo
- Combina resultados con pesos configurables
- Aplica reranking con modelo especializado
- Elimina duplicados manteniendo mejor score

#### 4. tool_regex_search
**Descripción**: Búsqueda por patrones regex

**Parámetros**:
```json
{
  "pattern": "string (requerido)",
  "file_types": "array<string> (opcional)",
  "case_sensitive": "boolean (opcional)",
  "max_matches_per_file": "integer (opcional)",
  "context_lines": "integer (opcional)"
}
```

**Mejoras V2**:
- Validación de patrones más robusta
- Cache de patrones frecuentes
- Límites de seguridad para evitar ReDoS

### Herramientas de Gestión de Documentos

#### 5. tool_get_document_structure (NUEVO)
**Descripción**: Recupera la estructura/tabla de contenidos de un documento

**Parámetros**:
```json
{
  "document_id": "string (requerido)",
  "include_summaries": "boolean (opcional)",
  "max_depth": "integer (opcional, default: 3)"
}
```

**Salida**:
```json
{
  "document_id": "doc_123",
  "document_name": "Manual_Usuario.pdf",
  "structure": {
    "type": "hierarchical",
    "sections": [
      {
        "id": "section_1",
        "title": "Introducción",
        "level": 1,
        "chunk_range": [0, 5],
        "summary": "Descripción general del sistema...",
        "subsections": [...]
      }
    ]
  },
  "total_sections": 15,
  "total_chunks": 120
}
```

**Implementación**:
- Análisis de estructura durante ingesta
- Almacenamiento en metadatos de OpenSearch
- Detección automática de jerarquía (títulos, numeración)

#### 6. tool_list_documents (NUEVO)
**Descripción**: Lista documentos disponibles con filtros

**Parámetros**:
```json
{
  "filters": {
    "file_types": "array<string> (opcional)",
    "date_range": "object (opcional)",
    "tags": "array<string> (opcional)",
    "search_term": "string (opcional)"
  },
  "sort_by": "name|date|size (opcional)",
  "page": "integer (opcional)",
  "page_size": "integer (opcional)"
}
```

**Salida**:
```json
{
  "total_documents": 245,
  "page": 1,
  "page_size": 20,
  "documents": [
    {
      "document_id": "doc_123",
      "name": "Manual_Usuario.pdf",
      "file_type": "pdf",
      "size_bytes": 2456789,
      "upload_date": "2025-01-15T10:30:00Z",
      "last_modified": "2025-01-20T14:22:00Z",
      "tags": ["manual", "usuario", "v2.0"],
      "chunk_count": 120,
      "summary": "Manual completo del sistema..."
    }
  ]
}
```

#### 7. tool_get_full_document
**Descripción**: Recupera el contenido completo de un documento

**Parámetros**:
```json
{
  "document_id": "string (requerido)",
  "format": "text|markdown|json (opcional)",
  "include_metadata": "boolean (opcional)"
}
```

**Mejoras V2**:
- Reconstrucción optimizada con manejo de overlaps
- Soporte para múltiples formatos de salida
- Streaming para documentos grandes
- Cache inteligente

#### 8. tool_get_document_section (NUEVO)
**Descripción**: Recupera una sección específica de un documento

**Parámetros**:
```json
{
  "document_id": "string (requerido)",
  "section_id": "string (opcional)",
  "section_query": "string (opcional)",
  "chunk_range": "object (opcional)",
  "include_context": "boolean (opcional)"
}
```

**Estrategias de selección**:
- Por `section_id`: Usa estructura precalculada
- Por `section_query`: Búsqueda semántica dentro del documento
- Por `chunk_range`: Acceso directo por rango de chunks

---

## 📥 MEJORAS EN EL PROCESO DE INGESTA

### Ingesta V1 (Actual)
- Chunking fijo por tamaño
- Embeddings básicos
- Metadatos limitados
- Sin análisis de estructura

### Ingesta V2 (Nueva)

#### 1. Chunking Inteligente
```python
class SmartChunker:
    """Chunking adaptativo basado en contenido"""
    
    strategies = {
        'semantic': SemanticChunker,      # Por coherencia semántica
        'structural': StructuralChunker,  # Por estructura (títulos, párrafos)
        'hybrid': HybridChunker,          # Combinación de ambos
        'sliding': SlidingWindowChunker   # Ventana deslizante con overlap
    }
    
    def chunk_document(self, document, strategy='hybrid'):
        """
        Aplica estrategia de chunking según tipo de documento
        
        - PDFs técnicos: structural (respeta secciones)
        - Documentos narrativos: semantic (coherencia)
        - Código: structural (funciones, clases)
        - Manuales: hybrid (estructura + semántica)
        """
        pass
```

**Características**:
- Respeta límites naturales (párrafos, secciones)
- Mantiene coherencia semántica
- Overlap configurable e inteligente
- Metadatos de posición precisos

#### 2. Análisis de Estructura
```python
class DocumentStructureAnalyzer:
    """Analiza y extrae estructura jerárquica"""
    
    def analyze(self, document):
        """
        Extrae:
        - Tabla de contenidos
        - Jerarquía de secciones
        - Títulos y subtítulos
        - Numeración y referencias
        - Imágenes y tablas
        """
        return {
            'toc': [...],
            'sections': [...],
            'images': [...],
            'tables': [...],
            'metadata': {...}
        }
```

**Almacenamiento**:
- Estructura en metadatos de OpenSearch
- Índice separado para navegación rápida
- Referencias cruzadas entre chunks

#### 3. Enriquecimiento de Metadatos
```python
metadata_schema = {
    # Metadatos básicos
    'document_id': 'uuid',
    'file_name': 'string',
    'file_type': 'string',
    'file_size': 'integer',
    'upload_date': 'datetime',
    'last_modified': 'datetime',
    
    # Metadatos de contenido
    'language': 'string',
    'encoding': 'string',
    'page_count': 'integer',
    'word_count': 'integer',
    
    # Metadatos de estructura
    'has_toc': 'boolean',
    'section_count': 'integer',
    'image_count': 'integer',
    'table_count': 'integer',
    
    # Metadatos de negocio
    'tags': 'array<string>',
    'category': 'string',
    'department': 'string',
    'confidentiality': 'string',
    
    # Metadatos de procesamiento
    'chunking_strategy': 'string',
    'chunk_count': 'integer',
    'embedding_model': 'string',
    'processing_version': 'string'
}
```

#### 4. Procesamiento de Imágenes
```python
class ImageProcessor:
    """Procesa imágenes embebidas en documentos"""
    
    def process_image(self, image_data):
        """
        - Extrae imágenes de PDFs/DOCX
        - Genera descripciones con Vision LLM
        - Crea embeddings multimodales
        - Almacena referencias en chunks
        """
        return {
            'image_id': 'uuid',
            'description': 'Generated description',
            'embedding': [vector],
            'location': 's3://bucket/images/...',
            'context': 'Surrounding text'
        }
```

#### 5. Pipeline de Ingesta V2
```
Documento → Extracción → Análisis Estructura → Chunking Inteligente
                                                        ↓
                                              Procesamiento Imágenes
                                                        ↓
                                              Generación Embeddings
                                                        ↓
                                              Enriquecimiento Metadatos
                                                        ↓
                                              Indexación OpenSearch
                                                        ↓
                                              Almacenamiento S3
                                                        ↓
                                              Validación y QA
```

---

## 🎨 MEJORAS EN LA INTERFAZ DE USUARIO

### Módulo 1: Chat Conversacional (Mejorado)

#### Funcionalidades Nuevas

**1. Subida de Archivos en Conversación**
```typescript
interface FileUploadFeature {
  // Tipos soportados
  supportedTypes: [
    'pdf', 'docx', 'xlsx', 'pptx',
    'txt', 'md', 'csv',
    'jpg', 'png', 'gif', 'webp'
  ];
  
  // Límites
  maxFileSize: '50MB';
  maxFilesPerMessage: 5;
  
  // Procesamiento
  processing: {
    immediate: boolean;      // Procesar inmediatamente
    addToKB: boolean;        // Añadir a base de conocimiento
    temporary: boolean;      // Solo para esta conversación
  };
  
  // UI
  dragAndDrop: true;
  progressIndicator: true;
  preview: true;
}
```

**Flujo de uso**:
1. Usuario arrastra archivo al chat
2. Sistema muestra preview y opciones
3. Usuario confirma procesamiento
4. Archivo se procesa y está disponible para consultas
5. Agente puede referenciar el archivo en respuestas

**2. Subida de Imágenes**
```typescript
interface ImageUploadFeature {
  // Procesamiento
  visionAnalysis: true;        // Análisis con Vision LLM
  ocrExtraction: true;         // OCR si contiene texto
  contextualEmbedding: true;   // Embedding multimodal
  
  // Consultas
  allowImageQueries: true;     // "¿Qué hay en esta imagen?"
  allowImageComparison: true;  // "Compara estas dos imágenes"
  allowImageSearch: true;      // "Busca imágenes similares"
}
```

**3. Copy to Clipboard**
```typescript
interface ClipboardFeature {
  // Opciones de copia
  copyOptions: {
    messageOnly: boolean;      // Solo el mensaje
    withContext: boolean;      // Con contexto de conversación
    formatted: boolean;        // Con formato markdown
    plainText: boolean;        // Texto plano
  };
  
  // UI
  copyButton: 'per-message';   // Botón en cada mensaje
