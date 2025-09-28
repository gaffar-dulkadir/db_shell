Important Note: 
zsh terminal:
"pip install 'pydantic[email]'
"


# Qdrant Database Management Service

A production-ready REST API service for managing Qdrant vector databases with comprehensive collection management, point operations, vector search capabilities, and automatic text-to-vector conversion using Ollama embedding service.

## 🚀 Features

- **Collection Management**: Create, update, delete, and manage Qdrant collections
- **Point Operations**: CRUD operations for vector points with batch support  
- **Material Indexing**: Automatic text-to-vector conversion using Ollama embedding service
- **Vector Search**: Similarity search, recommendations, and text-based semantic search
- **Administration**: Health checks, statistics, and monitoring
- **Generic & Reusable**: Domain-independent service suitable for any vector use case

## 📋 API Overview

### Base URL
```
http://localhost:8083
```

### API Documentation
- **Swagger UI**: `http://localhost:8083/docs`
- **ReDoc**: `http://localhost:8083/redoc`
- **OpenAPI JSON**: `http://localhost:8083/openapi.json`

## 🐳 Docker Compose Installation (Recommended)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Quick Start with Docker Compose

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vectordb-service
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables** (edit `.env` file):
   ```bash
   # Qdrant Configuration
   QDRANT_HOST=10.10.90.105
   QDRANT_PORT=6333

   # Ollama Embedding Service
   OLLAMA_HOST=localhost
   OLLAMA_PORT=80
   OLLAMA_BASE_URL=http://localhost
   EMBEDDING_MODEL=nomic-embed-text
   VECTOR_SIZE=2560

   # Application
   APP_PORT=8083
   APP_ENV=development
   ADMIN_API_KEY=admin123
   ```

4. **Start the service**
   ```bash
   # Start the service in detached mode
   docker-compose up -d

   # Or start with logs visible
   docker-compose up
   ```

5. **Verify the installation**
   ```bash
   # Check if service is running
   docker-compose ps

   # Check health
   curl http://localhost:8083/health

   # View logs
   docker-compose logs vectordb-service
   ```

6. **Access the API**
   - **API Documentation**: http://localhost:8083/docs
   - **Health Check**: http://localhost:8083/health
   - **Service Info**: http://localhost:8083/

### Docker Compose Management

```bash
# Stop the service
docker-compose down

# Restart the service
docker-compose restart

# View logs
docker-compose logs -f vectordb-service

# Update and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Remove everything (including volumes)
docker-compose down -v
```

## 🔧 Configuration

### Environment Variables

```bash
# Qdrant Configuration
QDRANT_HOST=10.10.90.105
QDRANT_PORT=6333

# Ollama Embedding Service Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=80
OLLAMA_BASE_URL=http://localhost
OLLAMA_API_URL=http://localhost/api
OLLAMA_EMBEDDINGS_URL=http://localhost/api/embeddings
OLLAMA_GENERATE_URL=http://localhost/api/generate
OLLAMA_CHAT_URL=http://localhost/api/chat
EMBEDDING_MODEL=nomic-embed-text
VECTOR_SIZE=2560

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8083
APP_ENV=development
APP_NAME="Qdrant Database Management Service"
APP_VERSION="2.0.0"

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE=logs/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Security & CORS
CORS_ORIGINS=*
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*
ADMIN_API_KEY=admin123
```

### Example .env file
```bash
QDRANT_HOST=10.10.90.105
QDRANT_PORT=6333

EMBEDDING_MODEL=nomic-embed-text
VECTOR_SIZE=2560

OLLAMA_HOST=localhost
OLLAMA_PORT=80
OLLAMA_BASE_URL=http://localhost
OLLAMA_API_URL=http://localhost/api
OLLAMA_EMBEDDINGS_URL=http://localhost/api/embeddings

APP_HOST=0.0.0.0
APP_PORT=8083
APP_ENV=development
LOG_LEVEL=INFO

ADMIN_API_KEY=admin123
APP_NAME="Qdrant Database Management Service"
APP_VERSION="2.0.0"
```

## 📚 API Endpoints

### 🏠 Root & Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API root information |
| `GET` | `/health` | Service health check |
| `GET` | `/admin/health` | Detailed health check |

### 📦 Collection Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/collections` | List all collections |
| `POST` | `/collections` | Create a new collection |
| `GET` | `/collections/{name}` | Get collection details |
| `PUT` | `/collections/{name}` | Update collection metadata |
| `DELETE` | `/collections/{name}` | Delete a collection |
| `GET` | `/collections/{name}/stats` | Get collection statistics |
| `HEAD` | `/collections/{name}` | Check if collection exists |

### 📄 Point Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/collections/{name}/points` | Create multiple points |
| `POST` | `/collections/{name}/points/single` | Create single point |
| `GET` | `/collections/{name}/points` | List points (paginated) |
| `GET` | `/collections/{name}/points/{id}` | Get specific point |
| `PUT` | `/collections/{name}/points/{id}` | Update point |
| `DELETE` | `/collections/{name}/points/{id}` | Delete point |

### 🔍 Search Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/collections/{name}/search` | Vector similarity search |
| `POST` | `/collections/{name}/search/text` | Text-based semantic search |
| `POST` | `/collections/{name}/search/recommend` | Get recommendations |
| `GET` | `/collections/{name}/search/similar/{id}` | Find similar to point |

### 📚 Material Indexing (Auto-Embedding)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/collections/{name}/index/material` | Index single material with auto-embedding |
| `POST` | `/collections/{name}/index/materials/batch` | Batch index materials |
| `POST` | `/collections/{name}/index/text` | Quick text indexing |

### 🔧 Administration

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/admin/stats` | Service statistics | ✅ |
| `GET` | `/admin/collections` | Collection summary | ✅ |
| `GET` | `/admin/qdrant` | Qdrant information | ✅ |
| `GET` | `/admin/system` | System information | ✅ |

## 🚀 Manual Installation (Alternative)

### 1. Prerequisites
- Python 3.8+
- Qdrant running on specified host:port
- Ollama embedding service running
- Poetry or pip for dependency management

### 2. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or using poetry
poetry install
```

### 3. Configuration
```bash
# Copy environment file
cp .env.example .env

# Edit configuration
nano .env
```

### 4. Run the Service
```bash
# Development mode
python src/app.py

# Or using uvicorn directly
uvicorn src.app:app --host 0.0.0.0 --port 8083 --reload
```

### 5. Verify Installation
```bash
# Check health
curl http://localhost:8083/health

# Get API info
curl http://localhost:8083/
```

## 📖 Usage Examples

### Create a Collection
```bash
curl -X POST "http://localhost:8083/collections" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-collection",
    "vector_size": 768,
    "distance": "Cosine",
    "description": "Sample collection for AI embeddings",
    "metadata": {
      "created_by": "user",
      "purpose": "semantic_search"
    }
  }'
```

### Add Points (Manual Vectors)
```bash
curl -X POST "http://localhost:8083/collections/my-collection/points" \
  -H "Content-Type: application/json" \
  -d '{
    "points": [
      {
        "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
        "payload": {
          "title": "Sample Document",
          "content": "This is a sample document",
          "category": "technology"
        }
      }
    ]
  }'
```

### Index Material with Auto-Embedding
```bash
curl -X POST "http://localhost:8083/collections/my-collection/index/material" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a material about machine learning algorithms and their applications.",
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

### Text-Based Semantic Search
```bash
curl -X POST "http://localhost:8083/collections/my-collection/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "machine learning algorithms",
    "limit": 5,
    "score_threshold": 0.6
  }'
```

### Vector Similarity Search
```bash
curl -X POST "http://localhost:8083/collections/my-collection/search" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
    "limit": 10,
    "score_threshold": 0.7,
    "with_payload": true
  }'
```

### Get Collection Statistics
```bash
curl "http://localhost:8083/collections/my-collection/stats"
```

## 🔒 Authentication

Admin endpoints require authentication via the `X-API-Key` header:

```bash
curl -X GET "http://localhost:8083/admin/stats" \
  -H "X-API-Key: admin123"
```

## 📊 Response Formats

### Success Response (Point)
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

### Error Response
```json
{
  "detail": "Error message",
  "error": "Detailed error information"
}
```

### Search Response
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

### Material Indexing Response
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
    "content": "This is a material about machine learning algorithms...",
    "content_length": 91,
    "indexed_at": 1756799636.672035,
    "author": "Data Scientist",
    "difficulty": "intermediate",
    "tags": ["machine-learning", "algorithms"]
  }
}
```

## 🔧 Development

### Project Structure
```
vectordb-service/
├── src/
│   ├── app.py                 # Application entry point
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging setup
│   ├── datalayer/
│   │   ├── database.py        # Database connections
│   │   ├── model/
│   │   │   ├── qdrant_models.py    # Domain models
│   │   │   └── dto/
│   │   │       ├── qdrant_dto.py   # API DTOs
│   │   │       └── business_logic_dto.py # Business DTOs
│   │   ├── repository/
│   │   │   └── qdrant_repository.py # Data access
│   │   └── mapper/
│   │       └── material_indexing_mapper.py # Data transformation
│   ├── services/              # Business logic
│   │   ├── collection_service.py
│   │   ├── point_service.py
│   │   ├── search_service.py
│   │   ├── material_indexing_service.py
│   │   ├── embedding_service.py
│   │   └── admin_service.py
│   └── routes/                # API endpoints
│       ├── collection_routes.py
│       ├── point_routes.py
│       ├── search_routes.py
│       ├── indexing_routes.py
│       └── admin_routes.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

### Adding New Features
1. Update DTOs in `datalayer/model/dto/`
2. Implement business logic in `services/`
3. Add API endpoints in `routes/`
4. Update documentation

## 🔍 Monitoring & Logging

### Health Checks
- Basic health: `GET /health`
- Detailed health: `GET /admin/health` (admin auth required)
- Service stats: `GET /admin/stats` (admin auth required)

### Logging
- Console output during development
- File logging: `logs/app.log`
- Structured JSON logs in production
- Configurable log levels and rotation

### Metrics
- Request/response times
- Error rates
- Collection statistics
- Vector count monitoring
- Embedding service performance

## 🐛 Troubleshooting

### Common Issues

1. **Qdrant Connection Failed**
   ```bash
   # Check Qdrant is running
   curl http://10.10.90.105:6333/health
   
   # Verify configuration
   echo $QDRANT_HOST $QDRANT_PORT
   
   # Check Docker network connectivity
   docker-compose logs vectordb-service
   ```

2. **Ollama Embedding Service Issues**
   ```bash
   # Check Ollama service is running
   curl http://localhost/api/embeddings
   
   # Verify embedding model is available
   curl http://localhost/api/tags
   
   # Check Ollama configuration
   echo $OLLAMA_HOST $EMBEDDING_MODEL
   ```

3. **Docker Compose Issues**
   ```bash
   # Check service status
   docker-compose ps
   
   # View detailed logs
   docker-compose logs --tail=50 vectordb-service
   
   # Restart with clean build
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **Import Errors (Manual Installation)**
   ```bash
   # Ensure you're in the right directory
   cd vectordb-service
   python -m src.app
   
   # Check Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

5. **Permission Denied (Admin endpoints)**
   ```bash
   # Check admin API key is set
   echo $ADMIN_API_KEY
   
   # Include in request header
   curl -H "X-API-Key: $ADMIN_API_KEY" http://localhost:8083/admin/stats
   ```

6. **Vector Size Mismatch**
   ```bash
   # Check collection vector size
   curl http://localhost:8083/collections/my-collection
   
   # Verify embedding model vector size
   echo $VECTOR_SIZE
   
   # Create collection with correct vector size
   curl -X POST "http://localhost:8083/collections" \
     -H "Content-Type: application/json" \
     -d '{"name": "test", "vector_size": 2560, "distance": "Cosine"}'
   ```

## 🏗️ Architecture Overview

The service provides high-level abstractions for vector database operations including:

- **Automatic text-to-vector conversion** using Ollama embedding service
- **Material indexing** with rich metadata support
- **Semantic search capabilities** for text queries
- **Production-ready** with comprehensive error handling and monitoring

### Key Features:
- ✅ Auto-generated UUIDs for all points
- ✅ Ollama integration for embedding generation
- ✅ Comprehensive collection management
- ✅ Flexible point operations with batch support
- ✅ Text-based semantic search capabilities
- ✅ Admin functionality with authentication

### External Dependencies:
- **Qdrant Database**: Vector storage and similarity search
- **Ollama Service**: Text-to-vector embedding generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- 📧 Email: support@yourcompany.com
- 📖 Documentation: `/docs`
- 🐛 Issues: GitHub Issues
- 🚀 Quick Start: Use Docker Compose for fastest setup