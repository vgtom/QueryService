# SQL Query Manager

A modern backend system for storing, analyzing, and optimizing SQL queries with AI assistance.

## System Design & Architecture

### Problem Interpretation

The core requirements were understood as:

1. **Query Management**: A system to store and retrieve SQL queries with metadata
2. **Lineage Analysis**: Extract table/column dependencies from queries
3. **AI-Powered Optimization**: Use AI to suggest query improvements

Key assumptions made:
- Queries are valid SQL statements
- User authentication is required for all operations
- Performance and scalability are important considerations
- System should be maintainable and observable

### Incremental Development Approach

#### v0 (Current Implementation)
- Basic CRUD operations for queries
- Simple SQL parsing using sqlglot
- Mock AI integration
- Basic authentication
- In-memory SQLite database
- Basic logging

#### v1 (Current Implementation)
- Redis caching for frequently accessed queries
- Improved SQL parsing with sqlglot
- Structured logging with request tracking
- JWT authentication
- Error handling and monitoring

#### v2 (Future Plans)
- PostgreSQL for production database
- Distributed caching with Redis Cluster
- Real OpenAI integration with retry mechanisms
- Query performance metrics collection
- Advanced lineage analysis with query plan parsing
- API rate limiting and quota management

#### v3 (Scale)
- Horizontal scaling with database sharding
- Read replicas for query retrieval
- Async processing for heavy operations
- Advanced monitoring with Prometheus/Grafana
- Distributed tracing with OpenTelemetry

### Architectural Decisions & Trade-offs

1. **FastAPI Framework**
   - Pros: Modern, async support, automatic OpenAPI docs
   - Cons: Newer ecosystem compared to Flask/Django

2. **SQLAlchemy ORM**
   - Pros: Database agnostic, powerful querying
   - Cons: Performance overhead compared to raw SQL

3. **Redis Caching**
   - Pros: Fast, supports TTL, distributed deployment
   - Cons: Additional infrastructure, cache invalidation complexity

4. **sqlglot Parser**
   - Pros: More reliable than string parsing, supports multiple dialects
   - Cons: May not handle all edge cases, performance overhead

### Performance & Scalability

Current implementation includes:
- Redis caching for frequent queries
- Database connection pooling
- Efficient SQL parsing with fallback mechanism

Future scaling strategies:
1. **Database Scaling**   ```python
   # Example sharding strategy
   def get_shard(user_id: str) -> str:
       shard_key = hash(user_id) % NUM_SHARDS
       return f"postgresql://user:pass@shard-{shard_key}/db"   ```

2. **Caching Strategy**   ```python
   # Multi-level caching
   class CacheService:
       def get(self, key: str):
           # Try local cache
           value = self.local_cache.get(key)
           if value:
               return value
           
           # Try Redis cache
           value = self.redis.get(key)
           if value:
               self.local_cache.set(key, value)
               return value
           
           return None   ```

### AI Integration Strategy

Current implementation:
- Mock AI service for development
- Basic error handling
- Simple suggestion format

Future improvements:
1. **Rate Limiting**   ```python
   class AIService:
       def __init__(self):
           self.rate_limiter = RateLimiter(max_calls=60, time_window=60)
           
       async def get_suggestions(self, query):
           async with self.rate_limiter:
               return await self._call_openai(query)   ```

2. **Response Validation**   ```python
   def validate_ai_response(response: Dict) -> bool:
       required_fields = ['suggestions', 'optimized_query']
       return all(field in response for field in required_fields)   ```

### Debugging & Observability

Current implementation includes:
- Structured logging with request tracking
- Error handling middleware
- Request/response logging

Future improvements:
1. **Metrics Collection**   ```python
   class MetricsMiddleware:
       def __init__(self):
           self.query_counter = Counter('sql_queries_total', 'Total queries processed')
           self.query_duration = Histogram('query_duration_seconds', 'Query processing time')   ```

2. **Distributed Tracing**   ```python
   class TracingMiddleware:
       async def __call__(self, request: Request, call_next):
           with tracer.start_span() as span:
               span.set_tag('user_id', request.user_id)
               response = await call_next(request)
               return response   ```

### Use of AI Tools

During development, I used:

1. **Claude AI**
   - Initial project structure design
   - Code generation for basic components
   - Documentation assistance

2. **GitHub Copilot**
   - Code completion for repetitive patterns
   - Test case generation
   - Error handling suggestions

The tools were particularly helpful for:
- Boilerplate code generation
- SQL parsing logic
- Authentication setup
- Documentation structure

## Getting Started

### Prerequisites
- Python 3.8+
- Redis server
- Virtual environment

### Installation 
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export SQL_QUERY_MANAGER_SECRET_KEY="your-secret-key"
export OPENAI_API_KEY="your-openai-key"  # Optional for v1
```

### Running the Application
```bash
# Start Redis server
redis-server

# Run the application
uvicorn app.main:app --reload
```

### Testing

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_services.py

# Run with coverage
pytest --cov=app tests/
```

#### Test Structure

The test suite includes:

1. **Unit Tests**
   - Query service tests
   - Lineage extraction tests
   - Cache service tests
   - Authentication tests

2. **Integration Tests**
   - API endpoint tests
   - Database integration tests
   - Redis integration tests

3. **Performance Tests**
   - Query parsing benchmarks
   - Cache hit/miss ratios
   - Response time measurements

#### Example Test Cases

Let's create some basic test files: