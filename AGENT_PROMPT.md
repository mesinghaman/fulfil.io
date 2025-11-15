# Professional Product Importer - AI Agent Generation Prompt

## Project Overview
Create a professional, enterprise-grade **Product Importer** web application that allows users to upload CSV files containing product data and import them into a database with real-time progress tracking, comprehensive error handling, and webhook notifications.

## Core Requirements

### 1. **Technology Stack**
- **Backend**: FastAPI (Python 3.12+)
- **Database**: SQLite with SQLAlchemy ORM (PostgreSQL compatible)
- **Frontend**: Vanilla HTML/CSS/JavaScript with Server-Sent Events
- **File Processing**: Pandas for CSV handling
- **Architecture**: Clean layered architecture (API → Services → Models)

### 2. **Key Features**
- **CSV Upload**: Handle files up to 500K records with drag-and-drop interface
- **Real-time Progress**: Server-Sent Events for live progress updates with percentage and record counts
- **Bulk Operations**: Optimized batch processing (5000 records/batch) with duplicate detection
- **Product Management**: Full CRUD operations with search, filtering, and pagination
- **Webhook System**: Configurable webhooks for event notifications
- **Data Validation**: SKU-based deduplication (case-insensitive) and data normalization

### 3. **Professional Architecture**
```
app/
├── __init__.py              # Package metadata
├── main.py                  # FastAPI application entry point
├── api/                     # API layer
│   ├── __init__.py
│   └── products.py          # RESTful endpoints
├── models/                  # Data layer
│   ├── __init__.py
│   └── database.py          # SQLAlchemy models
├── services/                # Business logic layer
│   ├── __init__.py
│   └── product_service.py   # Core business operations
└── utils/                   # Utility functions

tests/
├── unit/                    # Unit tests with mocks
└── integration/             # API integration tests

docs/                        # Comprehensive documentation
static/                      # CSS/JS assets
templates/                   # Jinja2 HTML templates
```

### 4. **Database Schema**
```sql
-- Products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    sku VARCHAR UNIQUE NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Webhooks table  
CREATE TABLE webhooks (
    id INTEGER PRIMARY KEY,
    url VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5. **API Endpoints**
- `GET /` - Upload interface
- `POST /upload-direct` - Async CSV upload with task ID
- `GET /progress/{task_id}` - SSE progress stream
- `POST /cancel/{task_id}` - Cancel import operation
- `GET /products` - Paginated product listing with search/filter
- `DELETE /products-all` - Bulk delete with confirmation
- `GET /status` - Database statistics
- `GET /webhooks` - Webhook management interface

### 6. **Performance Optimizations**
- **Async Processing**: Non-blocking uploads using ThreadPoolExecutor
- **Bulk Database Operations**: Raw SQL for batch inserts (5000 records/batch)
- **Memory Efficiency**: Stream processing for large files
- **Progress Tracking**: Real-time updates via SSE with cancellation support
- **Smart Pagination**: Efficient database queries with search/filter

### 7. **User Interface Requirements**
- **Modern Design**: Clean, responsive interface with progress indicators
- **Drag & Drop**: File upload with visual feedback
- **Real-time Updates**: Live progress bar with percentage and record counts
- **Data Management**: Sortable, searchable product table with pagination
- **Error Handling**: User-friendly error messages and validation

### 8. **Code Quality Standards**
- **Type Hints**: Full type annotations throughout
- **Docstrings**: Comprehensive documentation for all functions/classes
- **Error Handling**: Proper exception handling with logging
- **Testing**: Unit tests with mocks and integration tests
- **Separation of Concerns**: Clear layer boundaries with dependency injection

### 9. **Testing Requirements**
- **Unit Tests**: Test business logic in isolation using mocks
- **Integration Tests**: Test API endpoints with database interactions
- **Test Coverage**: Comprehensive test suite with pytest
- **Fixtures**: Reusable test data and mock objects

### 10. **Additional Features**
- **Webhook Testing**: Include utility script for webhook testing
- **Progress Cancellation**: Allow users to cancel long-running imports
- **Data Validation**: Comprehensive CSV validation and error reporting
- **Logging**: Structured logging for debugging and monitoring

## Expected Deliverables

1. **Complete Application**: Fully functional web application
2. **Professional Structure**: Clean, maintainable codebase
3. **Comprehensive Tests**: Unit and integration test suite
4. **Documentation**: API docs, architecture overview, and setup instructions
5. **Configuration Files**: pytest.ini, requirements.txt, .gitignore
6. **Sample Data**: Example CSV file for testing

## Success Criteria
- Handle 500K+ record CSV files efficiently
- Real-time progress updates with <1 second latency
- Professional code quality with full type hints and documentation
- Comprehensive test coverage (>90%)
- Clean, intuitive user interface
- Production-ready error handling and logging

## Technical Constraints
- Use only specified technology stack
- Follow Python PEP 8 standards
- Implement proper async/await patterns
- Use SQLAlchemy ORM with raw SQL for performance-critical operations
- Ensure cross-platform compatibility (Windows, macOS, Linux)

Generate a complete, production-ready application that demonstrates enterprise-level Python development practices with clean architecture, comprehensive testing, and professional documentation.
