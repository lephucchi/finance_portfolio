# Architecture Guide - Finance Portfolio Backend

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Frontend (React/Vue)                       │
│                    Dashboard + Web Interface                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend (main.py)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Middleware Layer                                          │   │
│  │ - Request Logging (RequestLoggingMiddleware)             │   │
│  │ - Error Handling (ErrorHandlingMiddleware)               │   │
│  │ - CORS                                                    │   │
│  │ - GZIP Compression                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐ │
│  │ API Router (v1)                                             │ │
│  │ ├─ /health ────────────────────► health.py                │ │
│  │ ├─ /dashboard ─────────────────► dashboard.py              │ │
│  │ ├─ /market ────────────────────► market.py                │ │
│  │ ├─ /sentiment ──────────────────► sentiment.py             │ │
│  │ └─ /macro ─────────────────────► macro.py                 │ │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐ │
│  │ Services Layer (Business Logic)                             │ │
│  │ ├─ MarketService ───────────────► market_service.py        │ │
│  │ ├─ SentimentService ────────────► sentiment_service.py     │ │
│  │ ├─ MacroService ────────────────► macro_service.py         │ │
│  │ └─ AnalyticsService ────────────► analytics_service.py     │ │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐ │
│  │ Database Layer (Data Access)                                │ │
│  │ ├─ AthenaClient ────────────────► Query S3 Gold Layer       │ │
│  │ ├─ SupabaseClient ──────────────► Cache & Query Logs        │ │
│  │ └─ ConnectionPool ──────────────► Connection Management     │ │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────┬──────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │ AWS     │      │ Supabase │      │    S3    │
   │ Glue +  │      │          │      │ Gold     │
   │ Athena  │      │ Database │      │ Layer    │
   │         │      │          │      │          │
   │ Query   │      │ - Logs   │      │ Analytics│
   │ Engine  │      │ - Cache  │      │ Parquet  │
   └─────────┘      │ - Users  │      └──────────┘
                    └──────────┘
```

## Design Patterns Used

### 1. Microservices Architecture

Each service is independently deployable:
- **MarketService**: Stock market data handling
- **SentimentService**: News sentiment analysis
- **MacroService**: Economic indicators
- **AnalyticsService**: High-level insights

### 2. Dependency Injection

FastAPI's `Depends()` system injects services:

```python
@router.get("/stocks")
async def get_stocks(service: MarketService = Depends(get_market_service)):
    return service.get_stock_data(...)
```

### 3. Repository Pattern

Database clients act as data repositories:

```python
class AthenaClient:
    def query(sql): -> list  # Repository interface
    
class SupabaseClient:
    def get_cached_result(): -> dict  # Repository interface
```

### 4. Service Locator Pattern

Service factory creates and wires dependencies:

```python
def get_market_service() -> MarketService:
    athena = AthenaClient()
    supabase = SupabaseClient()
    return MarketService(athena, supabase)
```

## Data Flow

### Example: Get Stock Data Request

```
1. HTTP Request
   GET /api/v1/market/stocks?start_date=2025-10-01&end_date=2025-10-18

2. Route Handler (market.py)
   async def get_stock_data() -> ResponseModel

3. Service Layer (MarketService)
   service.get_stock_data(start_date, end_date, symbols)
   
4. Cache Check (SupabaseClient)
   cached = supabase.get_cached_result(query_hash)
   IF cached: return cached result
   
5. Query Execution (AthenaClient)
   results = athena.query(built_sql_query)
   
6. Cache Store (SupabaseClient)
   supabase.cache_result(query_hash, sql, results)
   
7. Response Transformation
   Convert to ResponseModel[list[StockDataResponse]]
   
8. HTTP Response
   {
       "success": true,
       "data": [...],
       "message": "Stock data retrieved successfully"
   }
```

## Layering

### API Layer
- Route handlers
- Request validation
- Response formatting
- HTTP concerns only

### Service Layer
- Business logic
- Data coordination
- Caching decisions
- Domain logic

### Database Layer
- Query execution
- Connection management
- Error handling
- Data access abstraction

### Data Layer
- S3 (Gold Layer Parquet)
- Supabase (Cache, Logs)
- AWS Glue Catalog (Metadata)

## SOLID Implementation Details

### Single Responsibility
```python
# ❌ WRONG - Mixed responsibilities
class DataService:
    def query_athena(self): pass
    def cache_result(self): pass
    def send_email(self): pass  # Business logic + notification

# ✅ CORRECT - Single responsibility
class MarketService:
    def get_stock_data(self): pass  # Business logic only

class NotificationService:
    def send_email(self): pass  # Notification only
```

### Open/Closed
```python
# ✅ CORRECT - Open for extension, closed for modification
class Service:
    def __init__(self, athena_client, supabase_client):
        # Can extend by providing different implementations
        # Without modifying Service class
        self.athena = athena_client
        self.supabase = supabase_client
```

### Liskov Substitution
```python
# ✅ CORRECT - Can substitute database clients
class DatabaseClient(ABC):
    @abstractmethod
    def query(self, sql: str): pass

class AthenaClient(DatabaseClient):
    def query(self, sql: str): pass  # Implementation

class MockClient(DatabaseClient):
    def query(self, sql: str): pass  # Can substitute for testing
```

### Interface Segregation
```python
# ✅ CORRECT - Segregated interfaces
class MarketService:
    # Only market-related methods
    def get_stock_data(self): pass
    def get_technical_indicators(self): pass

class SentimentService:
    # Only sentiment-related methods
    def get_sentiment_summary(self): pass
    def get_news_articles(self): pass
```

### Dependency Inversion
```python
# ✅ CORRECT - Depends on abstractions, not concretions
def get_market_service():
    # Returns abstract service
    athena = AthenaClient()  # Could be any implementation
    supabase = SupabaseClient()  # Could be any implementation
    return MarketService(athena, supabase)
```

## Scalability Considerations

### Horizontal Scaling
- Stateless services can be replicated
- Load balancer distributes requests
- Shared database layer (Supabase, S3)

### Caching Strategy
- 5-minute TTL for query results
- Cache invalidation via timestamp
- Reduces Athena query costs

### Query Optimization
- Partition pruning by date
- Limit result sets with pagination
- Use specific column selection

### Connection Pooling
- Reuse database connections
- Reduce connection overhead
- Configurable pool size

## Error Handling Strategy

### Graceful Degradation
```python
try:
    results = athena.query(sql)
except Exception as e:
    logger.error(f"Query failed: {e}")
    return {"success": False, "error": str(e)}
```

### Structured Logging
```python
logger.info("Query executed", extra={
    "query_id": query_id,
    "duration_ms": 1234,
    "rows": 100
})
```

### Request Tracking
- Each request gets unique ID
- Traced through all layers
- Helps debugging and monitoring

## Testing Strategy

### Unit Tests
- Mock database clients
- Test service logic in isolation
- Fast execution

### Integration Tests
- Test service + database layer
- Use test database
- Verify actual queries

### End-to-End Tests
- Test full request/response cycle
- Verify API contracts
- Slow but comprehensive

## Deployment

### Development
```bash
python main.py  # Auto-reload enabled
```

### Production (Docker)
```bash
docker-compose up -d  # Auto-restart on failure
```

### Environment Configuration
- All secrets in `.env` (never commit)
- Different configs for dev/staging/prod
- Settings loaded from environment

## Monitoring & Observability

### Structured Logging
- JSON format for parsing
- Includes request IDs
- Timestamps in ISO8601

### Metrics
- Request duration
- Query execution time
- Cache hit rate
- Error rates

### Health Checks
- `/health` endpoint
- Database connectivity
- Service readiness

## Future Enhancements

1. **Authentication & Authorization**
   - JWT token validation
   - Role-based access control
   - API key management

2. **Rate Limiting**
   - Per-user rate limits
   - Query complexity limits
   - Cost-based throttling

3. **Real-time Updates**
   - WebSocket connections
   - Server-sent events
   - Pub/sub messaging

4. **Advanced Caching**
   - Redis for distributed cache
   - Cache warming strategies
   - Invalidation patterns

5. **Async Processing**
   - Celery for background jobs
   - Query result streaming
   - Batch processing

6. **API Versioning**
   - Multiple API versions
   - Backward compatibility
   - Deprecation strategy

7. **Analytics & Reporting**
   - API usage analytics
   - Cost tracking
   - Performance monitoring

8. **Internationalization**
   - Multi-language support
   - Localized error messages
   - Currency formatting
