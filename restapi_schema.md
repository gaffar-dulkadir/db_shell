# Qdrant Database Management Service - REST API Architecture

## Overview

The Qdrant Database Management Service is a production-ready REST API for managing Qdrant vector databases with comprehensive collection, point, and search operations. The service provides high-level abstractions for vector database operations including automatic text-to-vector conversion, material indexing, and semantic search capabilities.

## Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     REST API Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Points    │  │ Collections │  │   Search    │       │
│  │   Routes    │  │   Routes    │  │   Routes    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │  Indexing   │  │    Admin    │                       │
│  │   Routes    │  │   Routes    │                       │
│  └─────────────┘  └─────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Point     │  │ Collection  │  │   Search    │       │
│  │  Service    │  │  Service    │  │  Service    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  Material   │  │   Admin     │  │ Embedding   │       │
│  │ Indexing    │  │  Service    │  │  Service    │       │
│  │  Service    │  └─────────────┘  └─────────────┘       │
│  └─────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer                                │
│  ┌─────────────┐                    ┌─────────────┐       │
│  │   Qdrant    │                    │   Material  │       │
│  │ Repository  │                    │  Indexing   │       │
│  └─────────────┘                    │   Mapper    │       │
│                                     └─────────────┘       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                    DTOs                             │ │
│  │  PointDto, CollectionDto, SearchDto, etc.          │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                External Services                           │
│  ┌─────────────┐              ┌─────────────┐             │
│  │   Qdrant    │              │   Ollama    │             │
│  │  Database   │              │ (Embedding) │             │
│  └─────────────┘              └─────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### 1. REST API Layer (`src/routes/`)
- **Point Routes**: CRUD operations for vector points
- **Collection Routes**: Collection management operations
- **Search Routes**: Vector similarity search and recommendations
- **Indexing Routes**: Material indexing with automatic embedding generation
- **Admin Routes**: Administrative operations and health checks

#### 2. Service Layer (`src/services/`)
- **PointService**: Business logic for point operations
- **CollectionService**: Collection management logic
- **SearchService**: Search algorithms and result processing
- **MaterialIndexingService**: Text-to-vector conversion and indexing
- **EmbeddingService**: Integration with embedding models (Ollama)
- **AdminService**: System administration and monitoring

#### 3. Data Layer (`src/datalayer/`)
- **Repositories**: Data access abstractions for Qdrant
- **DTOs**: Data Transfer Objects for API communication
- **Models**: Internal data models
- **Mappers**: Data transformation utilities

## API Endpoints

### Base URL
```
http://localhost:8083
```

### 1. Collections Management
#### Create Collection (Enhanced with Mandatory Metadata)
```bash
curl -X POST "http://localhost:8083/collections" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "my-collection",
    "vector_size": 768,
    "distance": "Cosine",
    "description": "Sample collection for AI embeddings and semantic search",
    "department": "Engineering",
    "team": "Backend",
    "project": "AI Enhancement Platform",
    "source_type": "confluence",
    "access_level": "internal",
    "content_type": "documentation",
    "tags": ["ai", "embeddings", "search"],
    "priority": "high",
    "metadata": {
      "created_by": "user",
      "purpose": "semantic_search",
      "model": "nomic-embed-text"
    },
    "is_active": true
  }'
```

**Mandatory Fields (11 required):**
- `collection_name`: Unique collection identifier
- `vector_size`: Vector dimensions (1-65536)
- `description`: Minimum 10 characters
- `department`: Department name (Engineering, Product, DevOps, etc.)
- `team`: Team name (Backend, Mobile, Payment, etc.)
- `project`: Project identifier
- `source_type`: Data source (jira, confluence, gitlab, docs_wiki)
- `access_level`: Security level (public, internal, confidential)
- `content_type`: Content classification (issues, documentation, code, wiki)
- `tags`: Array of strings (minimum 1 tag required)
- `priority`: Priority level (high, medium, low)

**Optional Fields (4 with defaults):**
- `distance`: Distance metric (default: "Cosine")
- `metadata`: Additional JSON metadata (default: {})
- `created_date`: Auto-generated timestamp
- `is_active`: Active status (default: true)
```

**Response:**
```json
{
  "name": "my-collection",
  "vector_size": 768,
  "vectors_count": 0,
  "distance": "Cosine",
  "status": "green",
  "created_at": "2024-01-20T10:30:00Z",
  "description": "Sample collection for AI embeddings and semantic search",
  "metadata": {
    "created_by": "user",
    "purpose": "semantic_search",
    "model": "nomic-embed-text"
  },
  "department": "Engineering",
  "team": "Backend",
  "project": "AI Enhancement Platform",
  "sourceType": "confluence",
  "accessLevel": "internal",
  "contentType": "documentation",
  "tags": ["ai", "embeddings", "search"],
  "priority": "high",
  "isActive": true
}
```

#### List Collections
```bash
curl -X GET "http://localhost:8083/collections"
```

**Response:**
```json
[
  {
    "name": "my-collection",
    "vector_size": 768,
    "vectors_count": 150,
    "distance": "Cosine",
    "status": "green",
    "created_at": "2024-01-20T10:30:00Z",
    "description": "Sample collection for AI embeddings and semantic search",
    "metadata": {
      "created_by": "user",
      "purpose": "semantic_search",
      "model": "nomic-embed-text"
    },
    "department": "Engineering",
    "team": "Backend",
    "project": "AI Enhancement Platform",
    "sourceType": "confluence",
    "accessLevel": "internal",
    "contentType": "documentation",
    "tags": ["ai", "embeddings", "search"],
    "priority": "high",
    "isActive": true
  }
]
```

### 2. Point Operations

#### Create Single Point
```bash
curl -X POST "http://localhost:8083/collections/my-collection/points/single" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
    "payload": {
      "title": "Sample Document",
      "content": "This is a sample document",
      "category": "technology"
    }
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
  "payload": {
    "title": "Sample Document",
    "content": "This is a sample document",
    "category": "technology"
  }
}
```

#### Create Multiple Points
```bash
curl -X POST "http://localhost:8083/collections/my-collection/points" \
  -H "Content-Type: application/json" \
  -d '{
    "points": [
      {
        "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
        "payload": {
          "title": "Document 1",
          "content": "First document content"
        }
      },
      {
        "vector": [0.6, 0.7, 0.8, 0.9, 1.0],
        "payload": {
          "title": "Document 2",
          "content": "Second document content"
        }
      }
    ]
  }'
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
    "payload": {
      "title": "Document 1",
      "content": "First document content"
    }
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "vector": [0.6, 0.7, 0.8, 0.9, 1.0],
    "payload": {
      "title": "Document 2",
      "content": "Second document content"
    }
  }
]
```

#### Get Point
```bash
curl -X GET "http://localhost:8083/collections/my-collection/points/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
  "payload": {
    "title": "Sample Document",
    "content": "This is a sample document",
    "category": "technology"
  }
}
```

#### Update Point
```bash
curl -X PUT "http://localhost:8083/collections/my-collection/points/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.2, 0.3, 0.4, 0.5, 0.6],
    "payload": {
      "title": "Updated Document",
      "content": "This is an updated document",
      "category": "technology",
      "updated": true
    }
  }'
```

#### Delete Point
```bash
curl -X DELETE "http://localhost:8083/collections/my-collection/points/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "message": "Point '550e8400-e29b-41d4-a716-446655440000' deleted successfully"
}
```

#### List Points
```bash
curl -X GET "http://localhost:8083/collections/my-collection/points?limit=10&with_vectors=true"
```

**Response:**
```json
{
  "points": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
      "payload": {
        "title": "Document 1",
        "content": "First document content"
      }
    }
  ],
  "total": 1,
  "limit": 10,
  "next_offset": null,
  "has_more": false
}
```

### 3. Material Indexing (Auto-Embedding)

#### Index Single Material
```bash
curl -X POST "http://localhost:8083/collections/my-collection/index/material" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a single material content about machine learning algorithms and their applications.",
    "title": "ML Algorithms Guide",
    "source": "tech-documentation",
    "material_type": "document",
    "metadata": {
      "author": "Data Scientist",
      "difficulty": "intermediate",
      "tags": ["machine-learning", "algorithms"]
    }
  }'
```

**Response:**
```json
{
  "pointId": "f49ec6a2-c652-4aef-9e2b-80da84416671",
  "contentLength": 91,
  "vectorSize": 768,
  "title": "ML Algorithms Guide",
  "source": "tech-documentation",
  "materialType": "document",
  "metadata": {
    "title": "ML Algorithms Guide",
    "source": "tech-documentation",
    "material_type": "document",
    "content": "This is a single material content about machine learning algorithms and their applications.",
    "content_length": 91,
    "indexed_at": 1756799636.672035,
    "author": "Data Scientist",
    "difficulty": "intermediate",
    "tags": ["machine-learning", "algorithms"]
  }
}
```

#### Batch Index Materials
#### Batch Index Materials
```bash
curl -X POST "http://localhost:8083/collections/my-collection/index/materials/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "materials": [
      {
        "content": "First material about AI and machine learning concepts.",
        "title": "AI Introduction",
        "source": "tech-blog",
        "material_type": "article",
        "metadata": {
          "author": "John Doe",
          "category": "technology"
        }
      },
      {
        "content": "Second material about vector databases and semantic search.",
        "title": "Vector Databases Guide",
        "source": "tech-blog",
        "material_type": "article",
        "metadata": {
          "author": "Jane Smith",
          "category": "database"
        }
      }
    ]
  }'
```

**Response:**
```json
{
  "indexed_materials": [
    {
      "pointId": "2652c3f2-4088-5a28-b1ae-5ff2fd825971",
      "contentLength": 52,
      "vectorSize": 768,
      "title": "AI Introduction",
      "source": "tech-blog",
      "materialType": "article",
      "metadata": {
        "title": "AI Introduction",
        "source": "tech-blog",
        "material_type": "article",
        "content": "First material about AI and machine learning concepts.",
        "content_length": 52,
        "indexed_at": 1756799700.123456,
        "author": "John Doe",
        "category": "technology"
      }
    },
    {
      "pointId": "8a1b2c3d-4e5f-6789-abcd-ef0123456789",
      "contentLength": 59,
      "vectorSize": 768,
      "title": "Vector Databases Guide",
      "source": "tech-blog",
      "materialType": "article",
      "metadata": {
        "title": "Vector Databases Guide",
        "source": "tech-blog",
        "material_type": "article",
        "content": "Second material about vector databases and semantic search.",
        "content_length": 59,
        "indexed_at": 1756799700.234567,
        "author": "Jane Smith",
        "category": "database"
      }
    }
  ],
  "total_processed": 2,
  "processing_time_ms": 1250.5
}
```
#### Quick Text Indexing
```bash
curl -X POST "http://localhost:8083/collections/my-collection/index/text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "content=Quick text content for indexing&title=Quick Note&source=manual&material_type=note&metadata={\"priority\":\"high\"}"
```

### 4. Search Operations

#### Vector Search
```bash
curl -X POST "http://localhost:8083/collections/my-collection/search" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
    "limit": 5,
    "score_threshold": 0.7,
    "with_vector": false,
    "with_payload": true
  }'
```

**Response:**
```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "score": 0.95,
      "payload": {
        "title": "Document 1",
        "content": "First document content"
      }
    }
  ],
  "total": 1,
  "execution_time_ms": 15.2,
  "query_info": {
    "collection": "my-collection",
    "limit": 5,
    "score_threshold": 0.7
  }
}
```

#### Text Search (Auto-Embedding)
```bash
curl -X POST "http://localhost:8083/collections/my-collection/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "machine learning algorithms",
    "limit": 3,
    "score_threshold": 0.6
  }'
```

#### Find Similar Points
```bash
curl -X GET "http://localhost:8083/collections/my-collection/search/similar/550e8400-e29b-41d4-a716-446655440001?limit=5&score_threshold=0.7"
```

#### Recommendations
```bash
curl -X POST "http://localhost:8083/collections/my-collection/search/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "positive_ids": ["550e8400-e29b-41d4-a716-446655440001"],
    "negative_ids": ["550e8400-e29b-41d4-a716-446655440002"],
    "limit": 5,
    "with_payload": true
  }'
```

### 5. Administrative Operations

#### Health Check
```bash
curl -X GET "http://localhost:8083/admin/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "version": "2.0.0",
  "qdrant_status": "connected",
  "collections_count": 3,
  "total_vectors": 1500
}
```

#### Service Statistics
```bash
curl -X GET "http://localhost:8083/admin/stats"
```

**Response:**
```json
{
  "service_name": "Qdrant Database Management Service",
  "version": "2.0.0",
  "uptime_seconds": 3600.0,
  "collections": [
    {
      "name": "my-collection",
      "vectors_count": 150,
      "indexed_vectors_count": 150,
      "points_count": 150,
      "segments_count": 1,
      "disk_data_size": 1024000,
      "ram_data_size": 512000,
      "config": {}
    }
  ],
  "total_vectors": 150,
  "total_disk_usage": 1024000,
  "memory_usage": {
    "total_ram": 512000
  }
}
```

## Data Flow

### 1. Point Creation Flow
```
Client Request → Point Routes → Point Service → Qdrant Repository → Qdrant Database
                     ↓
                Response ← Point DTO ← Point Model ← Database Response
```

### 2. Material Indexing Flow
```
Client Request → Indexing Routes → Material Indexing Service → Embedding Service (Ollama)
                     ↓                        ↓
                Material DTO            Text → Vector
                     ↓                        ↓
                Point Service ← Vector + Metadata
                     ↓
              Qdrant Repository → Qdrant Database
                     ↓
                Response ← Indexing Response DTO
```

### 3. Search Flow
```
Client Request → Search Routes → Search Service → Embedding Service (if text search)
                     ↓                ↓                      ↓
                Search DTO      Query Vector            Text → Vector
                     ↓                ↓
              Qdrant Repository → Qdrant Database
                     ↓
                Response ← Search Results ← Similarity Results
```

## Key Features

### 1. Auto-Generated IDs
- All points receive auto-generated UUID identifiers
- No manual ID management required
- Consistent ID format across all operations

### 2. Automatic Text-to-Vector Conversion
- Seamless integration with Ollama embedding service
- Support for batch processing
- Multiple text formats and sources

### 3. Comprehensive Search
- Vector similarity search
- Text-based semantic search
- Recommendation engine
- Configurable similarity thresholds

### 4. Production Ready
- Comprehensive error handling
- Request validation
- Logging and monitoring
- Health checks and statistics

### 5. Flexible Data Model
- Rich metadata support
- Multiple material types
- Custom payload structures
- Extensible schema

## Configuration

### Environment Variables
```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
OLLAMA_HOST=http://3.64.5.81:80
EMBEDDING_MODEL=nomic-embed-text
PORT=8083
ENVIRONMENT=development
LOG_LEVEL=info
```

### Supported Vector Sizes
- Default: 768 dimensions
- Configurable per collection
- Range: 1-65536 dimensions

### Distance Metrics
- Cosine (default)
- Euclidean
- Dot Product

This architecture provides a scalable, maintainable, and feature-rich vector database management service with comprehensive REST API access to Qdrant's capabilities.