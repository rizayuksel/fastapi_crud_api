# FastAPI CRUD API

> A production-ready REST API with JWT authentication, Redis caching, and comprehensive testing.

## 🎯 Overview

This project is a case study demonstrating modern Python backend development practices. Built with FastAPI, it provides a complete authentication system, CRUD operations for item management, and analytics capabilities.

## ✨ Features

### Core Features
- **JWT Authentication** - Secure token-based auth with refresh tokens
- **User Management** - Registration, login, profile operations
- **Item CRUD** - Complete create, read, update, delete operations
- **Pagination & Filtering** - Efficient data retrieval with sorting
- **Soft Delete** - Data preservation with logical deletion
- **Analytics** - Category density analysis with aggregation

### Technical Features
- **Redis Caching** - 5-minute TTL cache for analytics endpoint
- **Global Error Handling** - Consistent error responses across all endpoints
- **Request Validation** - Pydantic schemas with comprehensive validation
- **Async Operations** - Non-blocking database operations
- **Custom Exceptions** - Clean error handling with specific exception types
- **Logging** - Structured logging for debugging and monitoring

## 🛠 Tech Stack

- **Framework:** FastAPI 0.129.0
- **Python:** 3.11.14
- **Database:** PostgreSQL 16 (AsyncSQLAlchemy 2.0+)
- **Cache:** Redis 7
- **Authentication:** JWT (python-jose 3.5.0) + Argon2 password hashing
- **Testing:** pytest with 83% coverage
- **Code Quality:** Black, Flake8, isort, pre-commit hooks
- **Container:** Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose V2

### Installation

1. **Clone repository**
```bash
git clone https://github.com/rizayuksel/fastapi_crud_api.git
cd fastapi_crud_api
```

2. **Configure environment**
```bash
cp .env.example .env
```

**Note:** Default values in `.env.example` work for local development. For production, generate a new `SECRET_KEY`:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

3. **Start services**
```bash
docker compose up -d --build
```

4. **Seed database (optional)**

The API works with an empty database, but you can seed it with sample data for testing:
```bash
make seed
```

This creates:
- 2 sample users (admin@example.com / Admin1234, john@example.com / John1234)
- 10 sample items across 5 categories (electronics, clothing, books, furniture, kitchen)

**Or** create data manually via Swagger UI at http://localhost:8000/docs

5. **Access API**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication
```
POST   /api/users/register      Register new user
POST   /api/users/login         Login and get tokens
POST   /api/users/refresh       Refresh access token
GET    /api/users/profile       Get current user profile
PATCH  /api/users/profile       Update user profile
```

### Items
```
GET    /api/items                                  List items (pagination, filtering, sorting)
POST   /api/items                                  Create new item
GET    /api/items/{id}                             Get item by ID
PATCH  /api/items/{id}                             Update item
DELETE /api/items/{id}                             Delete item (soft delete)
GET    /api/items/analytics/category-density       Category analysis
```

## 📖 Example Usage

### Register User
```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Create Item (with auth)
```bash
curl -X POST http://localhost:8000/api/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 14",
    "description": "Apple smartphone",
    "category": "electronics"
  }'
```

### List Items with Filtering
```bash
curl "http://localhost:8000/api/items?category=electronics&page=1&per_page=10&sort_by=created_at&order=desc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testing

### Run All Tests
```bash
make test
# or
docker compose exec api pytest app/tests/ -v
```

### Coverage Report
```bash
make coverage
# or
docker compose exec api pytest app/tests/ --cov=app --cov-report=term-missing
```

### Test Results
```
✅ 28 tests passing
✅ 83% code coverage
✅ All CRUD operations tested
✅ Authentication flow tested
✅ Error handling tested
```

<details>
<summary>📊 Detailed Coverage Report</summary>
```
Name                      Stmts   Miss  Cover
---------------------------------------------
app/cache.py                 35      5    86%
app/config.py                13      0   100%
app/database.py              18     10    44%
app/errors.py                14      2    86%
app/exceptions.py            12      0   100%
app/logging_config.py         7      0   100%
app/main.py                  25      7    72%
app/models.py                32      2    94%
app/routers/items.py         81     35    57%
app/routers/users.py         56     19    66%
app/schemas.py               75      4    95%
app/security.py              47      8    83%
app/tests/conftest.py        51      6    88%
---------------------------------------------
TOTAL                       690    119    83%
```
</details>

## 📁 Project Structure
```
fastapi_crud_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & startup
│   ├── config.py            # Settings management
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── security.py          # JWT & password utils
│   ├── cache.py             # Redis cache utilities
│   ├── exceptions.py        # Custom exceptions
│   ├── errors.py            # Global error handlers
│   ├── logging_config.py    # Logging setup
│   ├── routers/
│   │   ├── users.py         # User endpoints
│   │   └── items.py         # Item endpoints
│   └── tests/
│       ├── conftest.py      # Test fixtures
│       ├── test_users.py    # User tests
│       └── test_items.py    # Item tests
├── scripts/
│   └── seed_data.py         # Database seeding
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── Makefile
└── README.md
```

## 🎨 Design Decisions

### Why FastAPI over Django?
Having worked with Django extensively, I chose FastAPI for this project because:
- **Performance:** Async support for non-blocking I/O
- **Modern Python:** Native type hints and Pydantic validation
- **Auto Documentation:** Built-in Swagger UI
- **Lightweight:** Microservice-friendly architecture

### Why Soft Delete?
Items are marked as `is_deleted=True` rather than being removed from the database. This approach:
- Preserves data for auditing
- Enables data recovery
- Maintains referential integrity
- Supports undo operations

### Why Redis Cache?
Analytics endpoint uses aggregation queries that can be expensive. Redis cache:
- Reduces database load
- Improves response time
- Auto-invalidates on data changes
- Gracefully falls back if Redis is unavailable

### Why Custom Exceptions?
Instead of generic `HTTPException`, custom exceptions (`AppException`, `ResourceNotFoundError`, `AuthenticationError`) provide:
- Consistent error response format
- Better error tracking
- Type-safe error handling
- Cleaner code separation

## 🔧 Makefile Commands
```bash
make help       # Show all commands
make up         # Start containers
make down       # Stop containers
make restart    # Restart API
make logs       # View API logs
make shell      # Open shell in API container
make test       # Run tests
make coverage   # Run tests with coverage
make seed       # Seed database
make format     # Format code (black + isort)
make lint       # Run flake8
make clean      # Remove cache files
make reset      # Full reset (remove volumes)
```

## 🔒 Security Features

- **Password Hashing:** Argon2 (more secure than bcrypt)
- **JWT Tokens:** Short-lived access tokens (60 min)
- **Refresh Tokens:** Long-lived tokens (7 days) for token renewal
- **Token Validation:** Signature verification and expiration checks
- **Environment Variables:** Sensitive data in `.env` (gitignored)

## 📊 Performance Optimizations

- **Async/Await:** All database operations are non-blocking
- **Connection Pooling:** SQLAlchemy manages connection pool
- **Database Indexing:** Indexes on frequently queried fields
- **Redis Caching:** Expensive queries cached for 5 minutes
- **Pagination:** Efficient data retrieval with OFFSET/LIMIT

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Stop conflicting services or change ports in docker-compose.yml
docker compose down
lsof -i :8000  # Find process using port 8000
```

### Database Connection Issues
```bash
# Reset database
make reset
```

### Redis Connection Failed
```bash
# Check Redis status
docker compose exec redis redis-cli ping
# Should return: PONG
```

## 📝 Notes

This project was developed as a technical case study with focus on:
- Clean, readable code with professional standards
- Comprehensive testing and high coverage
- Production-ready patterns and practices
- Balance between functionality and maintainability

The codebase includes comments that reflect real developer thinking - balancing professionalism with personality!

## 📄 License

This project is created for educational and evaluation purposes.

---

**Built with ❤️ using FastAPI**
