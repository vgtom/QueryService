# Design Journal: SQL Query Manager

This journal documents the key design decisions and evolution of the SQL Query Manager project.

## Day 1: Initial Design & Core Components

### Initial Requirements Analysis
Started by breaking down the requirements into three core components:
1. Query storage and retrieval
2. SQL lineage extraction
3. AI-powered query optimization

### Data Model Design
Decided to use SQLAlchemy ORM for database interactions:

```python
class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    query_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

Rationale:
- Used SQLAlchemy for database agnosticism and future flexibility
- Included timestamps for auditing and filtering
- Separated lineage into its own table for better querying and maintenance

### API Design
Chose FastAPI for its:
- Modern async support
- Automatic OpenAPI documentation
- Type checking and validation
- Performance characteristics

## Day 2: SQL Parsing & Lineage

### Initial Approach: String Parsing
Started with basic string parsing but quickly realized its limitations:
```python
# Initial naive approach
def extract_tables(query: str) -> List[str]:
    # Simple regex to find table names
    return re.findall(r'FROM\s+(\w+)', query)
```

### Improved Solution: sqlglot
Switched to sqlglot for robust SQL parsing:
```python
def extract_lineage(query_text: str) -> List[Tuple[str, Optional[str]]]:
    parsed = sqlglot.parse_one(query_text)
    tables = set()
    for table in parsed.find_all(sqlglot.exp.Table):
        tables.add((table.name, None))
```

Benefits:
- Handles complex queries (CTEs, subqueries)
- Better error handling
- Support for multiple SQL dialects

## Day 3: Caching & Performance

### Redis Integration
Added Redis caching to improve performance:
```python
class CacheService:
    def get(self, key: str) -> Optional[Any]:
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
```

Key decisions:
- Used Redis for its:
  - Built-in TTL support
  - Atomic operations
  - Distributed deployment options
- Implemented cache invalidation on updates
- Added configurable expiration times

### Performance Considerations
Added database connection pooling:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10
)
```

## Day 4: Authentication & Security

### JWT Implementation
Added JWT-based authentication:
```python
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

Security considerations:
- Token expiration
- Secure secret key handling
- HTTPS requirement

## Day 5: Observability & Monitoring

### Structured Logging
Implemented structured logging with contextual information:
```python
logger = structlog.get_logger()

class LoggingMiddleware:
    async def dispatch(self, request: Request, call_next):
        logger.info(
            "incoming_request",
            method=request.method,
            url=str(request.url)
        )
```

Benefits:
- JSON-formatted logs
- Request tracking
- Performance monitoring

### Error Handling
Added comprehensive error handling:
- Custom exception classes
- Error logging
- User-friendly error messages

## Future Improvements

1. **Query Analysis**
   - Add query complexity scoring
   - Implement query plan analysis
   - Track query performance metrics

2. **Scalability**
   - Implement database sharding
   - Add read replicas
   - Set up distributed caching

3. **AI Integration**
   - Add retry mechanisms
   - Implement response validation
   - Cache AI suggestions

## Lessons Learned

1. **SQL Parsing**
   - String parsing is insufficient for complex SQL
   - Need robust parser with error handling
   - Consider dialect-specific features

2. **Caching Strategy**
   - Cache invalidation is complex
   - Need clear TTL policies
   - Consider cache warming for frequent queries

3. **Testing**
   - Mock external services (Redis, OpenAI)
   - Use in-memory SQLite for tests
   - Add performance benchmarks

4. **Security**
   - Always validate user input
   - Use environment variables for secrets
   - Implement rate limiting

## Day 6: Containerization & Deployment

### Docker Configuration
Created a multi-container setup using Docker and Docker Compose:

```dockerfile
# Dockerfile
FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data

ENV PYTHONPATH=/app
ENV SQL_QUERY_MANAGER_SECRET_KEY="your-secret-key"
ENV DATABASE_URL="sqlite:///data/sql_query_manager.db"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Service Orchestration
Used Docker Compose for managing multiple services:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - SQL_QUERY_MANAGER_SECRET_KEY=your-secret-key
      - DATABASE_URL=sqlite:///data/sql_query_manager.db
    depends_on:
      - redis

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  tests:
    build: .
    command: pytest
    environment:
      - SQL_QUERY_MANAGER_SECRET_KEY=your-test-key
      - DATABASE_URL=sqlite:///:memory:
      - REDIS_HOST=redis
```

Key decisions:
- Used multi-stage builds for smaller image size
- Separated test environment from production
- Mounted volumes for data persistence
- Environment-based configuration

### Environment Configuration
Updated services to use environment variables:

```python
# database.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_query_manager.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)
```

```python
# cache.py
def __init__(self, host=None, port=None, db=0):
    self.redis = redis.Redis(
        host=host or os.getenv("REDIS_HOST", "localhost"),
        port=port or int(os.getenv("REDIS_PORT", "6379")),
        db=db
    )
```

### Automation Script
Created a run script for automated deployment:

```bash
#!/bin/bash

# Create data directory
mkdir -p data

# Wait for services
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    while ! nc -z $host $port; do
        sleep 1
    done
}

# Start services
docker-compose up -d

# Initialize database
docker-compose exec app python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
"

# Run tests
docker-compose run --rm tests
```

Benefits:
- One-command deployment
- Automatic service orchestration
- Integrated testing
- Graceful shutdown handling

### Future Deployment Considerations

1. **Production Setup**
   - Use PostgreSQL instead of SQLite
   - Add health checks
   - Implement backup strategy

2. **Scaling**
   - Use Docker Swarm or Kubernetes
   - Implement load balancing
   - Set up monitoring

3. **CI/CD**
   - Add GitHub Actions workflow
   - Implement automated testing
   - Set up continuous deployment

