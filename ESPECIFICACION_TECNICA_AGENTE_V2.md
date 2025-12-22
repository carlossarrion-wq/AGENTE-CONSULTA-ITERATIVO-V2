# ESPECIFICACIÓN TÉCNICA - AGENTE DE CONSULTA ITERATIVO V2.0

**Proyecto**: Agente de Consulta Iterativo V2.0  
**Cliente**: Naturgy - Plataforma FactorIA  
**Versión**: 2.0  
**Fecha**: 22 de Diciembre de 2025  
**Estado**: Especificación Técnica Completa

---

## 📋 TABLA DE CONTENIDOS

1. [Introducción y Alcance](#1-introducción-y-alcance)
2. [Arquitectura General](#2-arquitectura-general)
3. [Sistema de Autenticación y Autorización](#3-sistema-de-autenticación-y-autorización)
4. [Base de Datos RDS PostgreSQL](#4-base-de-datos-rds-postgresql)
5. [Contrato de Datos con Proceso de Ingesta](#5-contrato-de-datos-con-proceso-de-ingesta)
6. [Herramientas del Agente (MCP Servers)](#6-herramientas-del-agente-mcp-servers)
7. [Arquitectura MCP](#7-arquitectura-mcp)
8. [Interfaz Web](#8-interfaz-web)
9. [Sistema Multi-Aplicación](#9-sistema-multi-aplicación)
10. [Estructura de Proyecto](#10-estructura-de-proyecto)
11. [Anexos](#11-anexos)

---

## 1. INTRODUCCIÓN Y ALCANCE

### 1.1 Descripción General

El Agente de Consulta Iterativo V2.0 es una evolución significativa del sistema actual (V1), diseñado para proporcionar capacidades avanzadas de búsqueda y consulta sobre bases de conocimiento corporativas. El sistema permite a los usuarios interactuar mediante lenguaje natural con documentación técnica, especificaciones funcionales y otros recursos de información almacenados en OpenSearch y S3.

Esta versión incorpora mejoras arquitectónicas fundamentales, incluyendo la migración a **Strands + Bedrock Agent Core**, implementación de herramientas como **servicios MCP independientes**, y un sistema robusto de autenticación basado en **IAM + JWT tokens**.

### 1.2 Objetivos del Proyecto

- **Modernizar la arquitectura** mediante Strands y Bedrock Agent Core
- **Mejorar la extensibilidad** con herramientas como servicios MCP
- **Fortalecer la seguridad** con autenticación IAM y autorización granular
- **Optimizar el acceso a información** con 8 herramientas especializadas
- **Mantener compatibilidad** con sistema multi-aplicación existente
- **Mejorar la trazabilidad** con registro completo en RDS PostgreSQL

### 1.3 Alcance del Proyecto

#### ✅ DENTRO DEL ALCANCE

- Agente conversacional con arquitectura Strands + Bedrock Agent Core
- 8 herramientas de búsqueda y acceso a información (como servicios MCP)
- Interfaz web con módulos de chat y gestión de documentos
- Sistema de autenticación IAM + JWT tokens
- Gestión multi-aplicación (Darwin, SAP, MuleSoft, etc.)
- Trazabilidad completa en RDS PostgreSQL
- Modo progresivo para documentos grandes
- Streaming y prompt caching
- Upload de archivos e imágenes en conversaciones
- Export y copy de conversaciones

#### ❌ FUERA DEL ALCANCE

- **Pipeline de ingesta** (se desarrolla por separado)
- **Versionado de documentos** (lo gestiona el proceso de ingesta)
- Procesamiento de documentos (chunking, embeddings, etc.)
- Generación de resúmenes y estructuras

### 1.4 Diferencias V1 vs V2

| Aspecto | V1 | V2 |
|---------|----|----|
| **Arquitectura** | Python monolítico | Strands + Agent Core + MCP |
| **Herramientas** | 4-6 herramientas integradas | 8 herramientas como servicios MCP |
| **Búsqueda** | Semántica, Léxica, Regex | + Híbrida, Estructura, Lista docs |
| **Interfaz** | CLI + Web básica | Web UI completa con features avanzadas |
| **Extensibilidad** | Código acoplado | MCP servers independientes |
| **Autenticación** | Username simple | IAM Roles + JWT tokens |
| **Autorización** | Básica | Granular (app + módulo) |
| **Trazabilidad** | Logs + JSON | RDS PostgreSQL completo |
| **Upload Files** | No | Sí (docs + imágenes) |
| **Export** | No | Sí (TXT, MD, JSON) |
| **Streaming** | Básico | Nativo con Strands |
| **Prompt Caching** | No | Sí (Haiku 4.5) |

---

## 2. ARQUITECTURA GENERAL

### 2.1 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIONES                              │
│                  (Multi-app: Darwin, SAP, MuleSoft...)               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼────────┐  ┌──────▼──────┐
            │  Autenticación │  │ Autorización │
            │  Lambda        │  │  Lambda      │
            │  (IAM + JWT)   │  │  (Permisos)  │
            └───────┬────────┘  └──────┬───────┘
                    │                  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │     API GW       │
                    │  (REST + WS)     │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  Chat Module   │  │  Document Mgr   │  │  Traceability  │
│  (Streaming)   │  │  (Existing)     │  │  (RDS Logger)  │
└───────┬────────┘  └────────┬────────┘  └───────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  AGENTE CORE     │
                    │  (Strands +      │
                    │  Agent Core)     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  MCP Protocol    │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  Search MCP    │  │  Document MCP   │  │  Utility MCP   │
│  Server        │  │  Server         │  │  Server        │
│  (Port 3000)   │  │  (Port 3001)    │  │  (Port 3002)   │
│                │  │                 │  │                │
│ • lexical      │  │ • file_section  │  │ • regex        │
│ • semantic     │  │ • file_content  │  │ • get_doc_list │
│ • hybrid       │  │                 │  │                │
│ • structure    │  │                 │  │                │
└───────┬────────┘  └────────┬────────┘  └───────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  OpenSearch    │  │      S3         │  │   RDS MySQL    │
│  (Vectores +   │  │  - documents/   │  │  (Trazabilidad)│
│   Léxico)      │  │  - Markdowns/   │  │                │
│                │  │  - HaikuSummary/│  │                │
│                │  │  - structures/  │  │                │
│                │  │  - snapshot/    │  │                │
└────────────────┘  └─────────────────┘  └────────────────┘
```

### 2.2 Componentes Principales

#### 2.2.1 Agente Core (Strands + Bedrock Agent Core)

**Responsabilidades**:
- Gestión de conversaciones y contexto
- Orquestación de herramientas MCP
- Streaming de respuestas
- Prompt caching
- Gestión de memoria conversacional

**Tecnologías**:
- **Strands**: Framework de agentes de AWS
- **Bedrock Agent Core**: Runtime de agentes
- **Modelo LLM**: Configurable (default: Claude Haiku 4.5)

**Características**:
- Soporte nativo de streaming
- Prompt caching para optimización
- **Gestión dinámica de contexto**: Mantiene hasta N turnos de conversación en memoria (configurable). Los turnos anteriores a N se eliminan automáticamente para no agotar la ventana de contexto del LLM.
- Integración con MCP protocol

#### 2.2.2 MCP Servers

**Arquitectura de Microservicios**:
- Cada servidor MCP es independiente
- Comunicación vía protocolo MCP estándar
- Escalabilidad horizontal
- Versionado independiente

**Servidores**:
1. **Search MCP Server** (Port 3000)
   - tool_lexical_search
   - tool_semantic_search
   - tool_hybrid_search

2. **Document MCP Server** (Port 3001)
   - tool_file_section
   - tool_file_content
   - tool_structure

3. **Utility MCP Server** (Port 3002)
   - tool_regex_search
   - tool_get_document_list

#### 2.2.3 Capa de Datos

**OpenSearch**:
- Índices por aplicación: `rag-documents-{app_name}`
- Vectores de 1024 dimensiones (Titan Embed Image V1)
- Búsqueda léxica (BM25) y semántica (KNN)

**S3**:
- Bucket por aplicación: `rag-system-{app_name}-{region}`
- 6 ubicaciones de datos (ver sección 5)
- Versionado gestionado por proceso de ingesta

**RDS PostgreSQL**:
- Endpoint: `rag-postgres.czuimyk2qu10.eu-west-1.rds.amazonaws.com`
- 12 tablas para trazabilidad completa
- Análisis y métricas de uso

### 2.3 Flujo de Datos

```
1. Usuario → API GW → Lambda Authenticator
   ↓
2. JWT Token generado → Cliente

3. Cliente → API GW (con JWT) → Lambda Authorizer
   ↓
4. Validación permisos → Agente Core

5. Agente Core → Analiza consulta → Selecciona herramienta(s)
   ↓
6. MCP Protocol → MCP Server → Ejecuta herramienta
   ↓
7. Resultado → Agente Core → Formatea respuesta
   ↓
8. Streaming → Cliente (WebSocket)
   ↓
9. Trazabilidad → RDS PostgreSQL

NOTA: El proceso puede ser iterativo entre los pasos 5-9. El agente puede 
ejecutar múltiples herramientas secuencialmente según sea necesario para 
responder completamente a la consulta del usuario.
```

---

## 3. SISTEMA DE AUTENTICACIÓN Y AUTORIZACIÓN

### 3.1 Flujo de Autenticación

```
┌──────────────────────────────────────────────────────────────┐
│                    FLUJO DE AUTENTICACIÓN                     │
└──────────────────────────────────────────────────────────────┘

1. Cliente → API GW: Access Key + Secret Key
                ↓
2. API GW → Lambda Authenticator
                ↓
3. Lambda Authenticator:
   - Valida credenciales con AWS STS (GetCallerIdentity)
   - Obtiene user_arn, account_id, user_id
   - Consulta IAM: GetUser + ListGroupsForUser
   - Obtiene políticas de usuario y grupos
   - Construye JWT Token con:
     * user_arn
     * account_id
     * user_id
     * groups (con sus políticas)
     * apps: {app: {modules: {module: [actions]}}}
     * exp (15 min después)
                ↓
4. Lambda Authenticator → Cliente: JWT Token
                ↓
5. Cliente → API GW: JWT Token (en headers)
                ↓
6. API GW → Lambda Authorizer:
   - Decodifica JWT Token
   - Verifica validez y caducidad
   - Compara con recurso solicitado
   - Retorna: {allowed: true/false, reason}
                ↓
7. Si allowed=true → Procesa request
   Si allowed=false → 403 Forbidden
```

### 3.2 Estructura de Políticas IAM

#### Nivel Aplicación

**Política de ejemplo**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AccessToKnowledgeBaseAgent",
    "Effect": "Allow",
    "Action": ["custom:Access", "custom:Read", "custom:Write"],
    "Resource": [
      "arn:aws:custom:eu-west-1:123456789012:application/knowledge-base-agent"
    ]
  }]
}
```

#### Nivel Módulo de Aplicación

**Política de ejemplo**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AccessToDocumentManagerModule",
    "Effect": "Allow",
    "Action": ["custom:Access", "custom:Read", "custom:Write"],
    "Resource": [
      "arn:aws:custom:eu-west-1:123456789012:application/knowledge-base-agent/module/document-manager"
    ]
  }]
}
```

### 3.3 Estructura JWT Token

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "user_arn": "arn:aws:iam::123456789012:user/john.doe",
  "account_id": "123456789012",
  "user_id": "AIDAI...",
  "apps": {
    "darwin": {
      "modules": {
        "chat": ["read", "write"],
        "document-manager": ["read", "write", "delete"]
      }
    },
    "sap": {
      "modules": {
        "chat": ["read"]
      }
    }
  },
  "groups": ["PowerUsers", "Viewers"],
  "iat": 1704067200,
  "exp": 1704068100
}
```

### 3.4 Implementación Lambda Authenticator

```python
import boto3
import jwt
import json
from datetime import datetime, timedelta

class LambdaAuthenticator:
    def __init__(self):
        self.sts_client = boto3.client('sts')
        self.iam_client = boto3.client('iam')
        self.secret_key = self._get_jwt_secret()
    
    def authenticate(self, access_key: str, secret_key: str) -> dict:
        """Autentica usuario y genera JWT token"""
        try:
            # 1. Validar credenciales con STS
            identity = self.sts_client.get_caller_identity()
            
            # 2. Obtener información del usuario
            user_arn = identity['Arn']
            account_id = identity['Account']
            user_id = identity['UserId']
            
            # 3. Obtener grupos y políticas
            username = user_arn.split('/')[-1]
            groups = self._get_user_groups(username)
            policies = self._get_user_policies(username, groups)
            
            # 4. Construir permisos granulares
            permissions = self._build_permissions(policies)
            
            # 5. Generar JWT token
            token = self._generate_jwt_token(
                user_arn=user_arn,
                account_id=account_id,
                user_id=user_id,
                groups=groups,
                permissions=permissions
            )
            
            return {
                'success': True,
                'token': token,
                'expires_in': 900
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_permissions(self, policies: list) -> dict:
        """
        Construye estructura de permisos granulares
        Formato: {app: {modules: {module: [actions]}}}
        """
        permissions = {}
        
        for policy in policies:
            for statement in policy.get('Statement', []):
                if statement['Effect'] != 'Allow':
                    continue
                
                for resource in statement.get('Resource', []):
                    parts = resource.split('/')
                    if len(parts) >= 2:
                        app_name = parts[1]
                        module_name = parts[3] if len(parts) >= 4 else 'chat'
                        
                        if app_name not in permissions:
                            permissions[app_name] = {'modules': {}}
                        
                        if module_name not in permissions[app_name]['modules']:
                            permissions[app_name]['modules'][module_name] = []
                        
                        actions = self._map_actions(statement.get('Action', []))
                        permissions[app_name]['modules'][module_name].extend(actions)
        
        return permissions
    
    def _generate_jwt_token(self, user_arn: str, account_id: str, 
                           user_id: str, groups: list, permissions: dict) -> str:
        """Genera JWT token"""
        payload = {
            'user_arn': user_arn,
            'account_id': account_id,
            'user_id': user_id,
            'apps': permissions,
            'groups': groups,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
```

### 3.5 Implementación Lambda Authorizer

```python
import jwt
import json

class LambdaAuthorizer:
    def __init__(self):
        self.secret_key = self._get_jwt_secret()
    
    def authorize(self, token: str, resource: str, action: str) -> dict:
        """
        Autoriza acceso a recurso
        
        Args:
            token: JWT token
            resource: Formato "app/module" (ej: "darwin/chat")
            action: "read", "write", "delete"
        """
        try:
            # 1. Decodificar y validar token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # 2. Parsear recurso solicitado
            app_name, module_name = resource.split('/')
            
            # 3. Verificar permisos
            if app_name not in payload.get('apps', {}):
                return {
                    'allowed': False,
                    'reason': f'No access to application: {app_name}'
                }
            
            app_perms = payload['apps'][app_name]
            if module_name not in app_perms.get('modules', {}):
                return {
                    'allowed': False,
                    'reason': f'No access to module: {module_name}'
                }
            
            module_actions = app_perms['modules'][module_name]
            if action not in module_actions:
                return {
                    'allowed': False,
                    'reason': f'Action {action} not allowed on {resource}'
                }
            
            # 4. Acceso permitido
            return {
                'allowed': True,
                'user_arn': payload['user_arn'],
                'user_id': payload['user_id']
            }
            
        except jwt.ExpiredSignatureError:
            return {'allowed': False, 'reason': 'Token expired'}
        except jwt.InvalidTokenError as e:
            return {'allowed': False, 'reason': f'Invalid token: {str(e)}'}
        except Exception as e:
            return {'allowed': False, 'reason': f'Authorization error: {str(e)}'}
```

---

## 4. BASE DE DATOS RDS POSTGRESQL

### 4.1 Información de Conexión

**Endpoint**: `rag-postgres.czuimyk2qu10.eu-west-1.rds.amazonaws.com`  
**Motor**: PostgreSQL  
**Región**: eu-west-1  
**Propósito**: Trazabilidad completa de interacciones y análisis de uso

> **NOTA IMPORTANTE**: El endpoint actual (`rag-postgres.czuimyk2qu10.eu-west-1.rds.amazonaws.com`) corresponde a la base de datos de la versión 1.0.
> 
> **Decisión pendiente**: Determinar si:
> - **Opción A**: Utilizar la misma BD (requiere backwards compatibility con V1)
> - **Opción B**: Crear nueva BD para V2.0 (permite refinar modelo sin restricciones)
> 
> **Recomendación**: Crear nueva BD V2.0 con modelo refinado, sin preocupación por backwards compatibility. El modelo actual es sólido pero podría optimizarse para las nuevas capacidades (ej: añadir campos para MCP servers, mejorar índices para análisis, etc.).

### 4.2 Esquema de Tablas

#### 4.2.1 web_users - Usuarios del sistema

```sql
CREATE TABLE public.web_users (
    id SERIAL PRIMARY KEY,
    access_key VARCHAR(255) NOT NULL UNIQUE,
    secret_key_hash VARCHAR(255) NOT NULL,
    user_name VARCHAR(255),
    user_arn VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    team VARCHAR(100),
    person_name VARCHAR(255),
    iam_group VARCHAR(255)
);

CREATE INDEX idx_users_iam_group ON web_users(iam_group);
CREATE INDEX idx_users_team ON web_users(team);
```

**Propósito**: Almacena información de usuarios autenticados con sus credenciales AWS y metadatos de IAM.

#### 4.2.2 web_sessions - Sesiones web activas

```sql
CREATE TABLE public.web_sessions (
    session_token VARCHAR(255) PRIMARY KEY,
    user_id INTEGER REFERENCES web_users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);
```

**Propósito**: Gestiona sesiones web con tokens JWT y tracking de actividad.

#### 4.2.3 user_sessions - Sesiones conversacionales

```sql
CREATE TABLE public.user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    conversation_summary TEXT,
    topics JSONB,
    entities JSONB,
    preferences JSONB
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_last_activity ON user_sessions(last_activity);
```

**Propósito**: Mantiene contexto de sesiones conversacionales con el agente.

#### 4.2.4 web_queries - Consultas del usuario

```sql
CREATE TABLE public.web_queries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES web_users(id),
    session_token VARCHAR(255) REFERENCES web_sessions(session_token),
    query_text TEXT NOT NULL,
    conversation_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    status VARCHAR(50) DEFAULT 'completed',
    confidence_score FLOAT,
    streaming_status VARCHAR(20) DEFAULT 'complete',
    llm_response TEXT,
    app_name VARCHAR(100),
    llm_trust_category VARCHAR(50),
    tools_used JSONB,
    tool_results JSONB,
    retrieved_docs_count INTEGER DEFAULT 0,
    response_timestamp TIMESTAMP,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_total INTEGER DEFAULT 0,
    conversation_id_bedrock VARCHAR(255),
    user_name VARCHAR(255),
    person_name VARCHAR(255),
    iam_group VARCHAR(255)
);

CREATE INDEX idx_queries_created_at ON web_queries(created_at DESC);
CREATE INDEX idx_queries_app_name ON web_queries(app_name);
CREATE INDEX idx_queries_confidence ON web_queries(confidence_score DESC);
CREATE INDEX idx_queries_response_time ON web_queries(response_time_ms);
CREATE INDEX idx_queries_trust_category ON web_queries(llm_trust_category);
CREATE INDEX idx_web_queries_user_name ON web_queries(user_name);
CREATE INDEX idx_web_queries_person_name ON web_queries(person_name);
CREATE INDEX idx_web_queries_iam_group ON web_queries(iam_group);
```

**Propósito**: Registro completo de cada consulta con métricas y tokens.

#### 4.2.5 tool_executions - Ejecuciones de herramientas

```sql
CREATE TABLE public.tool_executions (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES web_queries(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    tool_input JSONB,
    tool_output JSONB,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    iteration INTEGER DEFAULT 1,
    executed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tool_exec_query_id ON tool_executions(query_id);
CREATE INDEX idx_tool_exec_tool_name ON tool_executions(tool_name);
CREATE INDEX idx_tool_exec_success ON tool_executions(success);
CREATE INDEX idx_tool_exec_executed_at ON tool_executions(executed_at DESC);
```

**Propósito**: Tracking detallado de cada herramienta ejecutada.

#### 4.2.6 retrieved_documents - Documentos recuperados

```sql
CREATE TABLE public.retrieved_documents (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES web_queries(id) ON DELETE CASCADE,
    document_title VARCHAR(500),
    document_content TEXT,
    source_file VARCHAR(500),
    similarity_score FLOAT,
    rank_position INTEGER,
    tool_name VARCHAR(100),
    chunk_index INTEGER,
    total_chunks INTEGER,
    retrieved_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT retrieved_documents_query_rank UNIQUE (query_id, rank_position)
);

CREATE INDEX idx_retrieved_docs_query_id ON retrieved_documents(query_id);
CREATE INDEX idx_retrieved_docs_similarity ON retrieved_documents(similarity_score DESC);
CREATE INDEX idx_retrieved_docs_tool_name ON retrieved_documents(tool_name);
```

**Propósito**: Almacena documentos/chunks recuperados con scores.

#### 4.2.7 conversations - Historial conversacional

```sql
CREATE TABLE public.conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    confidence_score INTEGER,
    citations JSONB,
    reasoning JSONB,
    retrieval_info JSONB
);

CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);
```

**Propósito**: Historial completo de mensajes con metadatos enriquecidos.

#### 4.2.8 processed_documents - Documentos procesados

```sql
CREATE TABLE public.processed_documents (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    document_hash VARCHAR(64),
    processing_status VARCHAR(50) DEFAULT 'pending',
    chunks_count INTEGER DEFAULT 0,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP,
    file_size_bytes BIGINT,
    document_type VARCHAR(50),
    metadata JSONB,
    error_message TEXT
);

CREATE INDEX idx_processed_documents_name ON processed_documents(document_name);
CREATE INDEX idx_processed_documents_status ON processed_documents(processing_status);
CREATE INDEX idx_processed_documents_processed_at ON processed_documents(processed_at);
```

**Propósito**: Tracking de documentos procesados por ingesta.

#### 4.2.9 indexed_chunks - Chunks indexados

```sql
CREATE TABLE public.indexed_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(255) NOT NULL UNIQUE,
    document_id INTEGER REFERENCES processed_documents(id),
    opensearch_id VARCHAR(255),
    chunk_index INTEGER,
    content_preview TEXT,
    embedding_model VARCHAR(100),
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_indexed_chunks_document_id ON indexed_chunks(document_id);
CREATE INDEX idx_indexed_chunks_opensearch_id ON indexed_chunks(opensearch_id);
```

**Propósito**: Mapeo entre chunks en OpenSearch y documentos en RDS.

#### 4.2.10 document_downloads - Descargas de documentos

```sql
CREATE TABLE public.document_downloads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES web_users(id),
    document_title VARCHAR(500) NOT NULL,
    filename VARCHAR(255),
    file_size BIGINT,
    success BOOLEAN NOT NULL,
    ip_address INET,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_downloads_user_id ON document_downloads(user_id);
CREATE INDEX idx_document_downloads_created_at ON document_downloads(created_at);
```

**Propósito**: Auditoría de descargas de documentos.

#### 4.2.11 system_config - Configuración del sistema

```sql
CREATE TABLE public.system_config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Configuración dinámica del sistema.

#### 4.2.12 system_metrics - Métricas del sistema

```sql
CREATE TABLE public.system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC,
    metric_data JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_metrics_name_time ON system_metrics(metric_name, recorded_at);
```

**Propósito**: Métricas de rendimiento y uso del sistema.

### 4.3 Servicio de Trazabilidad

```python
import asyncpg
import json
from datetime import datetime

class TraceabilityService:
    """Servicio para registrar todas las interacciones en RDS PostgreSQL"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.connection_pool = None
    
    async def initialize(self):
        """Inicializa el pool de conexiones"""
        self.connection_pool = await asyncpg.create_pool(**self.db_config)
    
    async def log_query(self, query_data: dict) -> int:
        """Registra una nueva consulta del usuario"""
        async with self.connection_pool.acquire() as conn:
            query_id = await conn.fetchval("""
                INSERT INTO web_queries (
                    user_id, session_token, query_text, app_name,
                    user_name, person_name, iam_group, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                RETURNING id
            """, 
                query_data['user_id'],
                query_data['session_token'],
                query_data['query_text'],
                query_data['app_name'],
                query_data['user_name'],
                query_data['person_name'],
                query_data['iam_group']
            )
            return query_id
    
    async def log_tool_execution(self, tool_data: dict):
        """Registra ejecución de una herramienta"""
        async with self.connection_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO tool_executions (
                    query_id, tool_name, tool_input, tool_output,
                    execution_time_ms, success, error_message, iteration
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                tool_data['query_id'],
                tool_data['tool_name'],
                json.dumps(tool_data['tool_input']),
                json.dumps(tool_data['tool_output']),
                tool_data['execution_time_ms'],
                tool_data['success'],
                tool_data.get('error_message'),
                tool_data.get('iteration', 1)
            )
    
    async def update_query_response(self, query_id: int, response_data: dict):
        """Actualiza consulta con respuesta del agente"""
        async with self.connection_pool.acquire() as conn:
            await conn.execute("""
                UPDATE web_queries
                SET 
                    llm_response = $2,
                    response_time_ms = $3,
                    confidence_score = $4,
                    tokens_input = $5,
                    tokens_output = $6,
                    tokens_total = $7,
                    tools_used = $8,
                    retrieved_docs_count = $9,
                    response_timestamp = NOW(),
                    status = 'completed'
                WHERE id = $1
            """,
                query_id,
                response_data['llm_response'],
                response_data['response_time_ms'],
                response_data.get('confidence_score'),
                response_data['tokens_input'],
                response_data['tokens_output'],
                response_data['tokens_total'],
                json.dumps(response_data.get('tools_used', [])),
                response_data.get('retrieved_docs_count', 0)
            )
```

---

## 5. CONTRATO DE DATOS CON PROCESO DE INGESTA

### 5.1 Ubicaciones en S3

**Bucket**: `rag-system-{app_name}-{region}`

```
s3://rag-system-{app_name}-eu-west-1/
│
├── documents/                          # (1) Documentos originales
│   └── {subfolder}/
│       └── {filename}.{ext}
│
├── markdowns/                          # (2) Documentos procesados (formato .md)
│   └── {subfolder}/
│       └── {filename}.{ext}.md
│
├── summaries/                          # (3) Resúmenes generados
│   └── {subfolder}/
│       └── {filename}.{ext}_summary.json
│
├── structures/                         # (4) Estructuras de documentos
│   └── {subfolder}/
│       └── {filename}.{ext}_structure.json
│
└── snapshot/                           # (5) Inventario y versionado
    └── latest_state.json
```

### 5.2 Formato de Archivos

#### 5.2.1 Documento Markdown (.md)

**Ubicación**: `markdowns/{subfolder}/{filename}.{ext}.md`

**Contenido**:
- Documento completo en formato Markdown
- Preserva estructura, títulos, código, diagramas
- Optimizado para lectura y procesamiento por LLM

**Ejemplo**: `markdowns/02_Especificaciones_Funcionales/DOCUMENTACION_FLUJO_FACTURAS_SAP.docx.md`

#### 5.2.2 Resumen (_summary.json)

**Ubicación**: `summaries/{subfolder}/{filename}.{ext}_summary.json`

**Estructura**:
```
RESUMEN DEL DOCUMENTO: {filename}

PARTE 1:
--------------------------------------------------------------------------------
# RESUMEN EJECUTIVO: {título}

## DESCRIPCIÓN GENERAL
{descripción general del documento}

## PUNTOS CLAVE
- {punto clave 1}
- {punto clave 2}
...

## TEMAS PRINCIPALES
• **{Tema 1}**: {descripción}
• **{Tema 2}**: {descripción}
...

## INFORMACIÓN TÉCNICA RELEVANTE
{detalles técnicos importantes}

## ENTIDADES Y CONCEPTOS MENCIONADOS
{lista de entidades, sistemas, conceptos}

PARTE 2:
--------------------------------------------------------------------------------
[Continúa con más partes si el documento es extenso]
```

**Ejemplo**: `FD-Mulesoft_Funcional_summary.txt`

#### 5.2.3 Estructura (_structure.json)

**Ubicación**: `structures/{subfolder}/{filename}.{ext}_structure.json`

**Contenido**:
- Tabla de contenidos del documento en formato JSON
- Mapeo de secciones a chunks
- Metadata de navegación
- Información de jerarquía

**Ejemplo**: `structures/02_Especificaciones_Funcionales/FD-Mulesoft_Funcional.docx_structure.json`

#### 5.2.4 Inventario (latest_state.json)

**Ubicación**: `snapshot/latest_state.json`

**Estructura**:
```json
{
  "version": "3.0",
  "scan_date": "2025-12-18T13:27:05.486983",
  "bucket_name": "rag-system-mulesoft-eu-west-1",
  "documents": [
    {
      "filename": "FD-Mulesoft_Funcional.docx",
      "subfolder": "02_Especificaciones_Funcionales",
      "extension": ".docx",
      "size": 12479214,
      "has_md": true,
      "has_summary": true,
      "has_structure": true,
      "chunks_count": 45,
      "status": "COMPLETE",
      "md_key": "Markdowns/02_Especificaciones_Funcionales/FD-Mulesoft_Funcional.md",
      "summary_key": "HaikuSummary/02_Especificaciones_Funcionales/FD-Mulesoft_Funcional_summary.txt",
      "structure_key": "documents/02_Especificaciones_Funcionales/FD-Mulesoft_Funcional/structure/structure_summary.md",
      "source_file": "FD-Mulesoft_Funcional",
      "chunk_ids": [],
      "chunk_pattern": "FD-Mulesoft_Funcional_chunk_*"
    }
  ],
  "statistics": {
    "total": 7,
    "complete": 6,
    "partial": 1,
    "missing": 0,
    "indexed": 45,
    "with_md": 6,
    "with_summary": 6,
    "with_structure": 6
  },
  "opensearch_index": {
    "indexed_files": ["FD-Mulesoft_Funcional.docx"],
    "total_chunks": 45,
    "last_sync": "2025-12-18T13:27:05.486991",
    "sync_status": "OK"
  }
}
```

### 5.3 Información en OpenSearch

**Índice**: `rag-documents-{app_name}`

**Documento indexado**:
```json
{
  "chunk_id": "FD-Mulesoft_Funcional_chunk_0005",
  "file_name": "FD-Mulesoft_Funcional.docx",
  "file_path": "mulesoft/02_Especificaciones_Funcionales/FD-Mulesoft_Funcional.docx",
  "content": "Contenido del chunk...",
  "embedding_vector": [0.123, 0.456, ...],
  "chunk_index": 5,
  "chunk_start": 12500,
  "chunk_end": 15000,
  "overlap_info": {
    "has_overlap": true,
    "overlap_with_previous": 200,
    "overlap_with_next": 200
  },
  "metadata": {
    "file_extension": "docx",
    "file_size": 12479214,
    "processed_date": "2025-12-18T13:27:05",
    "app_name": "mulesoft",
    "document_type": "functional_spec",
    "section_title": "Arquitectura de Integración",
    "keywords": ["mulesoft", "apikit", "integración"]
  }
}
```

### 5.4 Contrato de Interfaz

El agente V2 **NO** gestiona el proceso de ingesta. El contrato entre ambos sistemas es:

**Responsabilidad del Proceso de Ingesta**:
- Procesar documentos originales
- Generar Markdowns
- Crear resúmenes con Haiku
- Generar estructuras
- Vectorizar y subir a OpenSearch
- Mantener `latest_state.json` actualizado
- Gestionar versionado de documentos

**Responsabilidad del Agente V2**:
- Leer datos de S3 (Markdowns, resúmenes, estructuras)
- Consultar OpenSearch (vectores + léxico)
- Presentar información al usuario
- NO modificar datos de ingesta

---

## 6. HERRAMIENTAS DEL AGENTE (MCP SERVERS)

### 6.1 Lista Completa de Herramientas

1. **tool_lexical_search** - Búsqueda por palabras exactas (BM25) - Origen: OpenSearch
2. **tool_semantic_search** - Búsqueda conceptual (embeddings) - Origen: OpenSearch
3. **tool_hybrid_search** - Búsqueda combinada ponderada - Origen: OpenSearch
4. **tool_structure** - Obtiene estructura del documento - Origen: S3
5. **tool_regex_search** - Búsqueda por patrones - Origen: OpenSearch
6. **tool_file_section** - Obtener chunks específicos - Origen: OpenSearch
7. **tool_file_content** - Obtener documento completo - Origen: S3
8. **tool_get_document_list** - Listar documentos disponibles - Origen: S3

### 6.2 Contratos de Herramientas

Cada herramienta tiene un contrato XML de entrada y formato de salida estructurado. Ver documento completo en `Contratos herramientas/TOOL_IO_CONTRACTS.md` para detalles exhaustivos.

#### 6.2.1 tool_lexical_search

**Entrada XML**:
```xml
<tool_lexical_search>
<query>términos de búsqueda</query>
<top_k>5</top_k>
</tool_lexical_search>
```

**Salida**: Resultados con score BM25, contenido truncado a ~500 chars, highlights.

#### 6.2.2 tool_semantic_search

**Entrada XML**:
```xml
<tool_semantic_search>
<query>pregunta conceptual</query>
<top_k>10</top_k>
<min_score>0.0</min_score>
</tool_semantic_search>
```

**Salida**: Resultados con similitud 0-1, contenido truncado a ~500 chars.

#### 6.2.3 tool_hybrid_search ⭐ NEW

**Entrada XML**:
```xml
<tool_hybrid_search>
<query>términos + conceptos</query>
<semantic_weight>0.6</semantic_weight>
<lexical_weight>0.4</lexical_weight>
<top_k>10</top_k>
</tool_hybrid_search>
```

**Salida**: Resultados combinados con score ponderado, muestra ambos scores.

**Implementación**:
```python
def hybrid_search(query: str, semantic_weight: float = 0.6, 
                 lexical_weight: float = 0.4, top_k: int = 10) -> dict:
    """Combina búsqueda semántica y léxica con scoring normalizado"""
    
    # 1. Ejecutar ambas búsquedas
    semantic_results = semantic_search(query, top_k=top_k * 2)
    lexical_results = lexical_search(query, top_k=top_k * 2)
    
    # 2. Normalizar scores (0-1)
    semantic_normalized = normalize_scores(semantic_results)
    lexical_normalized = normalize_scores(lexical_results)
    
    # 3. Combinar con pesos
    combined = {}
    for result in semantic_normalized:
        chunk_id = result['chunk_id']
        combined[chunk_id] = {
            'data': result,
            'score': result['score'] * semantic_weight
        }
    
    for result in lexical_normalized:
        chunk_id = result['chunk_id']
        if chunk_id in combined:
            combined[chunk_id]['score'] += result['score'] * lexical_weight
        else:
            combined[chunk_id] = {
                'data': result,
                'score': result['score'] * lexical_weight
            }
    
    # 4. Ordenar y retornar top_k
    sorted_results = sorted(
        combined.values(), 
        key=lambda x: x['score'], 
        reverse=True
    )[:top_k]
    
    return {
        'query': query,
        'total_found': len(sorted_results),
        'search_type': 'hybrid_search',
        'weights': {
            'semantic': semantic_weight,
            'lexical': lexical_weight
        },
        'results': [r['data'] for r in sorted_results]
    }
```

#### 6.2.4 tool_structure

**Descripción**: Obtiene la estructura del documento desde S3 en formato JSON.

**Entrada XML**:
```xml
<tool_structure>
<document_name>nombre_documento.ext</document_name>
</tool_structure>
```

**Salida**: Estructura completa del documento en formato JSON con tabla de contenidos, mapeo de secciones a chunks, y metadata de navegación.

**Fuente de Datos**: S3 (`structures/{subfolder}/{filename}.{ext}_structure.json`)

**Ejemplo de Salida**:
```json
{
  "document_name": "FD-Mulesoft_Funcional.docx",
  "total_chunks": 45,
  "structure": {
    "sections": [
      {
        "title": "1. Introducción",
        "chunks": [0, 1, 2],
        "subsections": []
      },
      {
        "title": "2. Arquitectura",
        "chunks": [3, 4, 5, 6],
        "subsections": [
          {
            "title": "2.1 Componentes",
            "chunks": [7, 8]
          }
        ]
      }
    ]
  }
}
```

#### 6.2.5 tool_regex_search

**Entrada XML**:
```xml
<tool_regex_search>
<predefined>email</predefined>
<context_lines>2</context_lines>
</tool_regex_search>
```

O con patrón personalizado:
```xml
<tool_regex_search>
<pattern>\bAPI[-_]?KEY\b</pattern>
<case_sensitive>true</case_sensitive>
</tool_regex_search>
```

**Salida**: Matches con contexto de líneas alrededor.

#### 6.2.6 tool_file_section

**Entrada XML**:
```xml
<tool_file_section>
<file_name>nombre_archivo.ext</file_name>
<chunk_start>5</chunk_start>
<chunk_end>10</chunk_end>
<include_metadata>true</include_metadata>
</tool_file_section>
```

**Salida**: Contenido **completo sin truncar** de chunks especificados.

#### 6.2.7 tool_file_content

**Entrada XML**:
```xml
<tool_file_content>
<file_name>nombre_archivo.ext</file_name>
<include_structure>true</include_structure>
</tool_file_content>
```

**Salida**: Documento **completo sin truncar** + estructura opcional.

**Modo Progresivo**:
```python
def get_full_document(file_name: str, force_full_content: bool = False,
                     max_size_threshold: int = 50000) -> dict:
    """
    Obtiene documento completo o estructura según tamaño
    
    Args:
        file_name: Nombre del archivo
        force_full_content: Forzar contenido completo
        max_size_threshold: Umbral en caracteres (default: 50K)
    """
    # 1. Obtener metadata del documento
    doc_info = get_document_info(file_name)
    
    # 2. Leer contenido desde S3 Markdown
    content = read_s3_markdown(doc_info['md_key'])
    
    # 3. Decidir modo
    if len(content) <= max_size_threshold or force_full_content:
        # Modo normal: devolver contenido completo
        return {
            'file_name': file_name,
            'mode': 'full_content',
            'content': content,
            'size': len(content),
            'structure': get_structure(file_name) if include_structure else None
        }
    else:
        # Modo progresivo: devolver solo estructura
        structure = get_structure(file_name)
        return {
            'file_name': file_name,
            'mode': 'progressive',
            'message': f'Documento grande ({len(content)} chars). Use tool_file_section para acceder a secciones específicas.',
            'size': len(content),
            'total_chunks': doc_info['chunks_count'],
            'structure': structure,
            'recommendation': 'Analice la estructura y solicite chunks específicos con tool_file_section'
        }
```

#### 6.2.8 tool_get_document_list ⭐ NEW

**Entrada XML**:
```xml
<tool_get_document_list>
<app_name>mulesoft</app_name>
<file_types>docx,md,pdf</file_types>
<sort_by>name</sort_by>
<include_stats>true</include_stats>
</tool_get_document_list>
```

**Salida**: Lista completa de documentos con metadata, estadísticas opcionales.

**Implementación**:
```python
def get_document_list(app_name: str, file_types: list = None,
                     sort_by: str = 'name', include_stats: bool = True) -> dict:
    """Lista documentos disponibles en la aplicación"""
    
    # 1. Leer latest_state.json desde S3
    snapshot = read_s3_json(f's3://rag-system-{app_name}-eu-west-1/snapshot/latest_state.json')
    
    # 2. Filtrar por tipo de archivo
    documents = snapshot['documents']
    if file_types:
        documents = [d for d in documents if d['extension'].lstrip('.') in file_types]
    
    # 3. Ordenar
    sort_keys = {
        'name': lambda d: d['filename'],
        'date': lambda d: d.get('processed_date', ''),
        'size': lambda d: d.get('size', 0),
        'chunks': lambda d: d.get('chunks_count', 0)
    }
    documents = sorted(documents, key=sort_keys.get(sort_by, sort_keys['name']))
    
    # 4. Preparar respuesta
    result = {
        'app_name': app_name,
        'total_documents': len(documents),
        'filters_applied': {
            'file_types': file_types or 'all',
            'sort_by': sort_by
        },
        'documents': documents
    }
    
    # 5. Agregar estadísticas si se solicitan
    if include_stats:
        result['statistics'] = calculate_statistics(documents)
    
    return result
```

### 6.3 Comparativa de Herramientas

| Herramienta | Origen | Tipo | Score | Contenido | Uso Principal |
|-------------|--------|------|-------|-----------|---------------|
| tool_lexical_search | **OpenSearch** | Palabras exactas | BM25 | Truncado 500 | Términos técnicos |
| tool_semantic_search | **OpenSearch** | Conceptual | 0-1 | Truncado 500 | Preguntas naturales |
| tool_hybrid_search | **OpenSearch** | Combinada | Ponderado | Truncado 500 | Mejor de ambos |
| tool_structure | **S3** | Estructura | N/A | JSON completo | Tabla de contenidos |
| tool_regex_search | **OpenSearch** | Patrones | N/A | Con contexto | Emails, códigos |
| tool_file_section | **OpenSearch** | Chunks | N/A | **Completo** | Secciones específicas |
| tool_file_content | **S3** | Documento | N/A | **Completo** | Documento entero |
| tool_get_document_list | **S3** | Inventario | N/A | Metadata | Exploración inicial |

---

## 7. ARQUITECTURA MCP

### 7.1 Protocolo MCP

**Model Context Protocol (MCP)** es un protocolo estándar para comunicación entre agentes LLM y herramientas externas.

**Características**:
- Comunicación bidireccional
- Descubrimiento automático de herramientas
- Schemas de entrada/salida tipados
- Versionado de herramientas
- Manejo de errores estandarizado

### 7.2 Servidores MCP

#### 7.2.1 Search MCP Server (Port 3000)

**Responsabilidades**:
- Búsquedas en OpenSearch
- Procesamiento de queries
- Normalización de scores
- Expansión de sinónimos

**Herramientas**:
- `tool_lexical_search`
- `tool_semantic_search`
- `tool_hybrid_search`

**Tecnologías**:
- Node.js / Python
- OpenSearch client
- Sentence Transformers (para embeddings)

**Configuración**:
```yaml
server:
  name: search-mcp-server
  version: 1.0.0
  port: 3000
  
opensearch:
  endpoint: ${OPENSEARCH_ENDPOINT}
  index_pattern: rag-documents-{app_name}
  
embedding:
  model: amazon.titan-embed-image-v1
  dimensions: 1024
  
search:
  default_top_k: 10
  max_top_k: 50
  content_truncate_length: 500
```

#### 7.2.2 Document MCP Server (Port 3001)

**Responsabilidades**:
- Acceso a documentos en S3
- Lectura de Markdowns
- Gestión de estructuras
- Modo progresivo

**Herramientas**:
- `tool_file_section`
- `tool_file_content`
- `tool_structure`

**Tecnologías**:
- Node.js / Python
- AWS SDK (S3)
- Markdown parser
- JSON parser

**Configuración**:
```yaml
server:
  name: document-mcp-server
  version: 1.0.0
  port: 3001
  
s3:
  bucket_pattern: rag-system-{app_name}-{region}
  region: eu-west-1
  
progressive_mode:
  enabled: true
  threshold_chars: 50000
  
cache:
  enabled: true
  ttl_seconds: 300
```

#### 7.2.3 Utility MCP Server (Port 3002)

**Responsabilidades**:
- Búsquedas regex
- Listado de documentos
- Utilidades generales

**Herramientas**:
- `tool_regex_search`
- `tool_get_document_list`

**Tecnologías**:
- Node.js / Python
- Regex engine
- S3 client

**Configuración**:
```yaml
server:
  name: utility-mcp-server
  version: 1.0.0
  port: 3002
  
regex:
  max_matches_per_file: 100
  context_lines: 2
  predefined_patterns:
    email: '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    url: 'https?://[^\s]+'
    version: '\d+\.\d+\.\d+'
```

### 7.3 Comunicación MCP

```
┌─────────────────┐
│  Agente Core    │
│  (Strands)      │
└────────┬────────┘
         │
         │ MCP Protocol
         │
    ┌────▼────┐
    │ MCP     │
    │ Client  │
    └────┬────┘
         │
    ┌────▼────────────────────────┐
    │                             │
┌───▼───┐  ┌────▼────┐  ┌────▼───┐
│Search │  │Document │  │Utility │
│Server │  │Server   │  │Server  │
└───────┘  └─────────┘  └────────┘
```

**Flujo de Comunicación**:
1. Agente analiza consulta del usuario
2. Selecciona herramienta apropiada
3. MCP Client envía request al servidor correspondiente
4. Servidor ejecuta herramienta
5. Servidor devuelve resultado estructurado
6. Agente formatea respuesta para el usuario

### 7.4 Ventajas de Arquitectura MCP

✅ **Extensibilidad**: Agregar nuevas herramientas sin modificar el agente  
✅ **Escalabilidad**: Cada servidor puede escalar independientemente  
✅ **Mantenibilidad**: Código desacoplado y modular  
✅ **Versionado**: Cada herramienta puede tener su propia versión  
✅ **Testing**: Pruebas unitarias por servidor  
✅ **Reutilización**: Servidores MCP pueden usarse en otros agentes  

---

## 8. INTERFAZ WEB

### 8.1 Módulos Principales

#### 8.1.1 Chat Module (Mejorado)

**Características**:
- Interfaz conversacional con streaming
- Soporte para markdown en respuestas
- Syntax highlighting para código
- Visualización de herramientas ejecutadas
- Indicadores de typing y procesamiento
- Historial de conversación
- **Upload de archivos** (PDF, DOCX, TXT, MD)
- **Upload de imágenes** (PNG, JPG, JPEG)
- **Copy to clipboard** de mensajes
- **Export conversation** (TXT, MD, JSON)

**Tecnologías**:
- React / Vue.js
- WebSocket para streaming
- Markdown renderer
- Syntax highlighter (Prism.js / Highlight.js)

**Componentes**:
```
ChatModule/
├── ChatInterface.tsx
├── MessageList.tsx
├── MessageItem.tsx
├── InputArea.tsx
├── FileUpload.tsx
├── ImageUpload.tsx
├── ToolExecutionIndicator.tsx
├── ExportDialog.tsx
└── CopyButton.tsx
```

#### 8.1.2 Document Manager Module (Existente)

**Características**:
- Listado de documentos disponibles
- Búsqueda y filtrado
- Visualización de metadata
- Descarga de documentos
- Gestión de permisos
- Estadísticas de uso

**Mejoras V2**:
- Integración con `tool_get_document_list`
- Vista de estructura de documentos
- Preview de resúmenes
- Indicadores de estado (COMPLETE, PARTIAL, MISSING)

### 8.2 Features Nuevas

#### 8.2.1 Upload de Archivos

**Formatos soportados**:
- Documentos: PDF, DOCX, TXT, MD
- Imágenes: PNG, JPG, JPEG, GIF

**Flujo**:
1. Usuario selecciona archivo
2. Upload a S3 temporal
3. Procesamiento inline (extracción de texto)
4. Inclusión en contexto de conversación
5. Limpieza automática después de sesión

**Límites**:
- Tamaño máximo: 10 MB por archivo
- Máximo 5 archivos por mensaje
- Formatos validados en cliente y servidor

#### 8.2.2 Copy to Clipboard

**Funcionalidad**:
- Botón "Copy" en cada mensaje del asistente
- Copia contenido en formato markdown
- Feedback visual de éxito
- Soporte para código con syntax

#### 8.2.3 Export Conversation

**Formatos**:
- **TXT**: Texto plano con timestamps
- **MD**: Markdown formateado
- **JSON**: Estructura completa con metadata

**Contenido exportado**:
- Todos los mensajes de la conversación
- Timestamps
- Herramientas ejecutadas
- Metadata de sesión

### 8.3 Arquitectura Frontend

```
┌──────────────────────────────────────┐
│         React Application            │
├──────────────────────────────────────┤
│  ┌────────────┐  ┌────────────────┐  │
│  │ Chat       │  │ Document       │  │
│  │ Module     │  │ Manager        │  │
│  └─────┬──────┘  └────────┬───────┘  │
│        │                  │          │
│  ┌─────▼──────────────────▼───────┐  │
│  │     State Management (Redux)   │  │
│  └─────┬──────────────────────────┘  │
│        │                             │
│  ┌─────▼──────────────────────────┐  │
│  │     API Client Layer           │  │
│  │  - REST API calls              │  │
│  │  - WebSocket connection        │  │
│  │  - File upload handler         │  │
│  └─────┬──────────────────────────┘  │
└────────┼──────────────────────────────┘
         │
    ┌────▼────┐
    │ API GW  │
    └─────────┘
```

---

## 9. SISTEMA MULTI-APLICACIÓN

### 9.1 Aplicaciones Soportadas

El sistema soporta múltiples bases de conocimiento independientes:

- **Darwin**: Sistema de contratación
- **SAP**: Documentación SAP
- **MuleSoft**: Integraciones y APIs
- **DeltaSmile**: Sistema específico
- **BPO MNC**: Procesos de negocio
- **SAP LCorp**: SAP corporativo

### 9.2 Configuración por Aplicación

Cada aplicación tiene su propia configuración:

```yaml
# config/config_{app_name}.yaml

app_name: darwin
display_name: "Darwin - Sistema de Contratación"

opensearch:
  index: rag-documents-darwin
  
s3:
  bucket: rag-system-darwin-eu-west-1
  region: eu-west-1

system_prompt_file: config/system_prompt_darwin.md

features:
  upload_files: true
  export_conversation: true
  document_manager: true
  
llm:
  model_id: anthropic.claude-3-haiku-20240307-v1:0
  temperature: 0.1
  max_tokens: 4096
  streaming: true
  prompt_caching: true

tools:
  enabled:
    - tool_lexical_search
    - tool_semantic_search
    - tool_hybrid_search
    - tool_structure
    - tool_regex_search
    - tool_file_section
    - tool_file_content
    - tool_get_document_list
```

### 9.3 System Prompts

Cada aplicación tiene un system prompt específico que define:

- **Rol del agente** en esa aplicación
- **Herramientas disponibles** y cuándo usarlas
- **Sinónimos y acrónimos** del dominio
- **Contexto específico** de la aplicación
- **Guías de respuesta** y formato

**Ejemplo** (`system_prompt_darwin.md`):

```markdown
# System Prompt - Darwin

Eres un asistente experto en el sistema Darwin de Naturgy, especializado en procesos de contratación de servicios energéticos.

## Tu Rol
- Ayudar a usuarios a encontrar información sobre procesos de contratación
- Explicar flujos de trabajo y procedimientos
- Proporcionar referencias a documentación técnica

## Herramientas Disponibles
1. **tool_semantic_search**: Para preguntas conceptuales
2. **tool_lexical_search**: Para términos técnicos específicos
3. **tool_hybrid_search**: Cuando necesites ambos enfoques
4. **tool_structure**: Para obtener tabla de contenidos
5. **tool_file_content**: Para ver documentos completos
6. **tool_get_document_list**: Para explorar documentos disponibles

## Sinónimos y Acrónimos
- Darwin = Sistema de Contratación
- FD = Ficha de Diseño / Documento Funcional
- CUPS = Código Universal del Punto de Suministro
- CIF = Código de Identificación Fiscal

## Guías de Respuesta
- Siempre cita las fuentes de información
- Usa formato markdown para claridad
- Incluye ejemplos cuando sea apropiado
- Si no encuentras información, dilo claramente
```

### 9.4 Selector de Aplicación

La interfaz web incluye un selector de aplicación:

```typescript
interface AppSelector {
  currentApp: string;
  availableApps: Application[];
  userPermissions: {
    [appName: string]: {
      modules: {
        [moduleName: string]: string[]; // actions
      };
    };
  };
}

// Usuario solo ve aplicaciones a las que tiene acceso
const visibleApps = availableApps.filter(app => 
  userPermissions[app.name] !== undefined
);
```

---

## 10. ESTRUCTURA DE PROYECTO

### 10.1 Organización de Carpetas

```
agente-consulta-v2/
├── README.md
├── .gitignore
├── package.json / requirements.txt
│
├── config/                          # Configuraciones
│   ├── config_darwin.yaml
│   ├── config_sap.yaml
│   ├── config_mulesoft.yaml
│   ├── system_prompt_darwin.md
│   ├── system_prompt_sap.md
│   └── system_prompt_mulesoft.md
│
├── src/
│   ├── agent/                       # Agente Core (Strands)
│   │   ├── agent_core.py
│   │   ├── conversation_manager.py
│   │   ├── tool_orchestrator.py
│   │   └── streaming_handler.py
│   │
│   ├── auth/                        # Autenticación y Autorización
│   │   ├── lambda_authenticator.py
│   │   ├── lambda_authorizer.py
│   │   └── jwt_manager.py
│   │
│   ├── mcp_servers/                 # Servidores MCP
│   │   ├── search_server/
│   │   │   ├── server.py
│   │   │   ├── lexical_search.py
│   │   │   ├── semantic_search.py
│   │   │   └── hybrid_search.py
│   │   │
│   │   ├── document_server/
│   │   │   ├── server.py
│   │   │   ├── file_section.py
│   │   │   ├── file_content.py
│   │   │   ├── tool_structure.py
│   │   │   └── progressive_mode.py
│   │   │
│   │   └── utility_server/
│   │       ├── server.py
│   │       ├── regex_search.py
│   │       └── document_list.py
│   │
│   ├── traceability/                # Trazabilidad RDS
│   │   ├── traceability_service.py
│   │   ├── db_models.py
│   │   └── analytics.py
│   │
│   ├── web/                         # Interfaz Web
│   │   ├── frontend/
│   │   │   ├── src/
│   │   │   │   ├── components/
│   │   │   │   │   ├── Chat/
│   │   │   │   │   └── DocumentManager/
│   │   │   │   ├── services/
│   │   │   │   ├── store/
│   │   │   │   └── App.tsx
│   │   │   └── package.json
│   │   │
│   │   └── backend/
│   │       ├── api_gateway.py
│   │       ├── websocket_handler.py
│   │       └── file_upload_handler.py
│   │
│   └── utils/                       # Utilidades
│       ├── s3_client.py
│       ├── opensearch_client.py
│       ├── config_loader.py
│       └── logger.py
│
├── tests/                           # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/                            # Documentación
│   ├── ESPECIFICACION_TECNICA_AGENTE_V2.md
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── USER_GUIDE.md
│
└── infrastructure/                  # IaC
    ├── terraform/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    │
    └── cloudformation/
        └── stack.yaml
```

### 10.2 Dependencias Principales

**Backend (Python)**:
```txt
# Agent Core
strands-sdk>=1.0.0
boto3>=1.34.0
anthropic>=0.18.0

# MCP
mcp-sdk>=1.0.0
fastapi>=0.109.0
uvicorn>=0.27.0

# Data Access
opensearch-py>=2.5.0
asyncpg>=0.29.0
aioboto3>=12.3.0

# Auth
pyjwt>=2.8.0
cryptography>=42.0.0

# Utils
pydantic>=2.6.0
python-dotenv>=1.0.0
loguru>=0.7.0
```

**Frontend (TypeScript/React)**:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "@reduxjs/toolkit": "^2.0.0",
    "react-redux": "^9.0.0",
    "react-markdown": "^9.0.0",
    "prismjs": "^1.29.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.6.0"
  }
}
```

---

## 11. ANEXOS

### 11.1 Glosario de Términos

**Agente Core**: Componente central que gestiona conversaciones y orquesta herramientas

**BM25**: Algoritmo de ranking para búsqueda léxica

**Chunk**: Fragmento de documento procesado y vectorizado

**Embedding**: Representación vectorial de texto

**IAM**: Identity and Access Management de AWS

**JWT**: JSON Web Token para autenticación

**KNN**: K-Nearest Neighbors para búsqueda semántica

**MCP**: Model Context Protocol

**OpenSearch**: Motor de búsqueda y análisis

**Prompt Caching**: Optimización que reutiliza partes del prompt

**RAG**: Retrieval-Augmented Generation

**RDS**: Relational Database Service de AWS

**Strands**: Framework de agentes de AWS

**Streaming**: Envío progresivo de respuestas

### 11.2 Referencias

**Documentación AWS**:
- [Bedrock Agent Core](https://docs.aws.amazon.com/bedrock/)
- [Strands Framework](https://github.com/awslabs/strands)
- [OpenSearch](https://docs.aws.amazon.com/opensearch-service/)
- [RDS PostgreSQL](https://docs.aws.amazon.com/rds/)

**Protocolos y Estándares**:
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [OAuth 2.0](https://oauth.net/2/)

**Modelos LLM**:
- [Claude 3 Haiku](https://www.anthropic.com/claude)
- [Titan Embeddings](https://aws.amazon.com/bedrock/titan/)

### 11.3 Contactos del Proyecto

**Equipo Técnico**:
- Arquitecto: [Nombre]
- Tech Lead Backend: [Nombre]
- Tech Lead Frontend: [Nombre]
- DevOps Lead: [Nombre]

**Stakeholders**:
- Product Owner: [Nombre]
- Sponsor: [Nombre]
- Usuario Clave Darwin: [Nombre]
- Usuario Clave SAP: [Nombre]

### 11.4 Control de Cambios

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 22/12/2025 | Equipo Técnico | Versión inicial completa |

---

## CONCLUSIÓN

Esta especificación técnica define completamente el Agente de Consulta Iterativo V2.0, una evolución significativa que moderniza la arquitectura, mejora la extensibilidad mediante MCP servers, fortalece la seguridad con IAM + JWT, y proporciona una experiencia de usuario superior con 8 herramientas especializadas y features avanzadas.

El sistema está diseñado para ser escalable, mantenible y extensible, con una clara separación de responsabilidades entre el proceso de ingesta (fuera de alcance) y el agente de consulta.

La implementación seguirá un enfoque iterativo de 20 semanas, con hitos claros y entregables definidos, asegurando una transición suave desde la V1 y una adopción exitosa por parte de los usuarios.

---

**Documento**: ESPECIFICACION_TECNICA_AGENTE_V2.md  
**Versión**: 2.0  
**Fecha**: 22 de Diciembre de 2025  
**Estado**: Completo y Aprobado para Implementación
