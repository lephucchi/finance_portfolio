# Finance Portfolio API Documentation

## API Overview

**Finance Portfolio Dashboard API** is a FastAPI backend serving financial analytics dashboard with:
- Real-time market data queries
- Sentiment analysis from news
- Macro economic indicators
- Advanced analytics and correlations

## Architecture

### Microservices Design

The backend is organized as independent microservices:

```
app/
├── api/               # REST API endpoints (v1)
├── services/          # Business logic (Market, Sentiment, Macro, Analytics)
├── db/                # Database clients (Athena, Supabase)
├── schemas/           # Pydantic models for validation
├── middleware/        # HTTP middleware (logging, error handling)
└── utils/             # Helper functions
```

### Data Flow

```
FastAPI Endpoint
    ↓
Route Handler
    ↓
Service Layer (Business Logic)
    ↓
Database Layer (Athena + Supabase)
    ↓
S3 Gold Layer (Parquet Data)
```

## Getting Started

### 1. Environment Setup

Create `.env` file in backend directory:

```env
# App
DEBUG=true
ENVIRONMENT=development

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=ap-southeast-1

# Athena
ATHENA_DATABASE=finance_portfolio
ATHENA_RESULTS_LOCATION=s3://bankanalystportfolio/athena_results/

# Supabase
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Development Server

```bash
python main.py
```

Server will start at `http://localhost:8000`

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### Health Check

```http
GET /api/v1/health
```

### Market Data

```http
GET /api/v1/market/stocks?start_date=2025-10-01&end_date=2025-10-18&symbols=ACB,VCB

GET /api/v1/market/technical-indicators?symbol=ACB&start_date=2025-10-01&end_date=2025-10-18

GET /api/v1/market/sector-performance?start_date=2025-10-01&end_date=2025-10-18
```

### Sentiment Analysis

```http
GET /api/v1/sentiment/summary?start_date=2025-10-01&end_date=2025-10-18

GET /api/v1/sentiment/articles?start_date=2025-10-01&end_date=2025-10-18&sentiment=positive

GET /api/v1/sentiment/trend?start_date=2025-10-01&end_date=2025-10-18&interval=daily
```

### Macro Indicators

```http
GET /api/v1/macro/indicators?start_date=2025-10-01&end_date=2025-10-18

GET /api/v1/macro/available-indicators

GET /api/v1/macro/indicator/GDP?start_date=2025-10-01&end_date=2025-10-18

GET /api/v1/macro/forex?start_date=2025-10-01&end_date=2025-10-18
```

### Dashboard

```http
GET /api/v1/dashboard/summary?date=2025-10-18

GET /api/v1/dashboard/correlation?start_date=2025-10-01&end_date=2025-10-18
```

## SOLID Principles Implementation

### 1. Single Responsibility Principle (SRP)

Each class has a single responsibility:

- **AthenaClient**: Only manages Athena queries
- **SupabaseClient**: Only manages Supabase operations
- **MarketService**: Only handles market data logic
- **SentimentService**: Only handles sentiment analysis

Example:
```python
class MarketService:
    """Only handles market data operations"""
    
    def __init__(self, athena_client: AthenaClient, supabase_client: SupabaseClient):
        self.athena = athena_client
        self.supabase = supabase_client
```

### 2. Open/Closed Principle (OCP)

Classes are open for extension, closed for modification:

```python
# Can extend ServiceBase without modifying existing services
class ServiceBase:
    def __init__(self, athena: AthenaClient, supabase: SupabaseClient):
        self.athena = athena
        self.supabase = supabase
```

### 3. Liskov Substitution Principle (LSP)

Database clients are interchangeable:

```python
service = MarketService(athena_client, supabase_client)
# Can be extended with other database clients maintaining same interface
```

### 4. Interface Segregation Principle (ISP)

Services expose only necessary methods:

```python
class MarketService:
    # Market-specific methods only
    def get_stock_data(...)
    def get_technical_indicators(...)
    def get_sector_performance(...)
```

### 5. Dependency Inversion Principle (DIP)

High-level modules depend on abstractions:

```python
# Services depend on client abstractions
def get_market_service() -> MarketService:
    athena = AthenaClient()  # Abstract dependency
    supabase = SupabaseClient()  # Abstract dependency
    return MarketService(athena, supabase)
```

## Project Structure Best Practices

```
backend/
├── app/                      # Application package
│   ├── __init__.py
│   ├── api/                  # REST endpoints
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py
│   │       │   ├── market.py
│   │       │   ├── sentiment.py
│   │       │   ├── macro.py
│   │       │   └── dashboard.py
│   │       └── __init__.py
│   ├── services/             # Business logic layer
│   │   ├── market_service.py
│   │   ├── sentiment_service.py
│   │   ├── macro_service.py
│   │   ├── analytics_service.py
│   │   └── __init__.py
│   ├── db/                   # Database layer
│   │   ├── athena_client.py
│   │   ├── supabase_client.py
│   │   ├── connection_pool.py
│   │   └── __init__.py
│   ├── schemas/              # Pydantic models
│   │   └── __init__.py
│   ├── middleware/           # HTTP middleware
│   │   └── __init__.py
│   ├── utils/                # Utilities
│   │   └── __init__.py
│   └── core/                 # Core config
│       ├── __init__.py
│       └── config.py
├── config/                   # Settings
│   ├── __init__.py
│   └── settings.py
├── tests/                    # Unit tests
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
└── .env                      # Environment variables
```

## Key Design Patterns

### 1. Dependency Injection

```python
@router.get("/stocks")
async def get_stock_data(
    service: MarketService = Depends(get_market_service)
) -> ResponseModel:
    pass
```

### 2. Service Layer Pattern

Separates business logic from HTTP handling:

```python
# Service (business logic)
class MarketService:
    def get_stock_data(self, start_date, end_date, symbols):
        pass

# Endpoint (HTTP handling)
@router.get("/stocks")
async def get_stock_data(service: MarketService = Depends()):
    return service.get_stock_data(...)
```

### 3. Factory Pattern

Creates service instances with dependencies:

```python
def get_market_service() -> MarketService:
    athena = AthenaClient()
    supabase = SupabaseClient()
    return MarketService(athena, supabase)
```

### 4. Repository Pattern

Database clients act as repositories:

```python
class AthenaClient:
    def query(self, sql: str) -> list[dict]:
        pass

class SupabaseClient:
    def get_cached_result(self, query_hash: str) -> Optional[dict]:
        pass
```

## Performance Considerations

### 1. Caching

- Query results cached in Supabase with 5-minute TTL
- Cache key is SHA256 hash of query
- Significantly reduces Athena costs

### 2. Partitioning

- All S3 data partitioned by date
- Athena only scans required partitions
- Dramatically improves query speed

### 3. Connection Pooling

- Maintain connection pool for database connections
- Reuse connections instead of creating new ones
- Reduces overhead and latency

## Monitoring and Logging

### Structured Logging

All logs are JSON formatted for easy parsing:

```json
{
  "timestamp": "2025-10-26T10:30:45.123456",
  "level": "INFO",
  "logger": "app.services.market_service",
  "message": "Fetching market data",
  "request_id": "abc-123",
  "duration_ms": 1234
}
```

### Request Tracking

Each request has unique ID for tracing:

```
x-request-id: abc-123-def-456
x-process-time: 0.1234
```

## Extending the API

### Adding New Endpoint

1. **Create endpoint file** in `app/api/v1/endpoints/`
2. **Create service** in `app/services/`
3. **Define schemas** in `app/schemas/`
4. **Add router** to `app/api/v1/__init__.py`

### Adding New Service

```python
# app/services/new_service.py
from app.db import AthenaClient, SupabaseClient

class NewService:
    def __init__(self, athena: AthenaClient, supabase: SupabaseClient):
        self.athena = athena
        self.supabase = supabase
```

## Deployment

### Docker

Build image:
```bash
docker build -t finance-api:latest .
```

Run container:
```bash
docker run -p 8000:8000 --env-file .env finance-api:latest
```

### Environment Variables

All configuration via `.env` file (never commit to git):

```
DEBUG=false
ENVIRONMENT=production
ATHENA_DATABASE=finance_portfolio
```

## Testing

Run tests:
```bash
pytest tests/
```

With coverage:
```bash
pytest --cov=app tests/
```

## Troubleshooting

### Athena Query Timeout

- Increase `ATHENA_MAX_WAIT_TIME` in settings
- Optimize queries to scan fewer partitions

### Supabase Connection Error

- Check `SUPABASE_URL` and `SUPABASE_KEY`
- Verify network connectivity

### S3 Access Denied

- Check AWS credentials in `.env`
- Verify IAM permissions for S3 bucket

## Contributing

1. Follow SOLID principles
2. Add type hints to all functions
3. Write docstrings for all classes/functions
4. Use consistent naming conventions
5. Run tests before committing

## License

Proprietary - Finance Portfolio Project
