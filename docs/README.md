# Product Importer Documentation

## Project Structure

```
app/
├── __init__.py              # Application package
├── main.py                  # FastAPI application entry point
├── api/                     # API routes
│   ├── __init__.py
│   └── products.py          # Product-related endpoints
├── core/                    # Core configuration
├── models/                  # Database models
│   ├── __init__.py
│   └── database.py          # SQLAlchemy models
├── services/                # Business logic
│   ├── __init__.py
│   └── product_service.py   # Product operations
└── utils/                   # Utility functions

tests/
├── __init__.py
├── unit/                    # Unit tests
│   └── test_product_service.py
└── integration/             # Integration tests
    └── test_api.py

docs/                        # Documentation
static/                      # Static files (CSS, JS)
templates/                   # HTML templates
```

## Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run tests:**
   ```bash
   pytest                    # All tests
   pytest tests/unit/        # Unit tests only
   pytest tests/integration/ # Integration tests only
   ```

3. **Code formatting:**
   ```bash
   black app/ tests/         # Format code
   flake8 app/ tests/        # Lint code
   mypy app/                 # Type checking
   ```

4. **Run application:**
   ```bash
   python -m app.main
   # or
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc

## Testing

The project includes comprehensive tests:

- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test API endpoints with database interactions
- **Fixtures**: Reusable test data and mock objects

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Code Quality

The project follows Python best practices:

- **Type hints**: All functions have proper type annotations
- **Docstrings**: Comprehensive documentation for all modules and functions
- **Error handling**: Proper exception handling and logging
- **Separation of concerns**: Clear separation between API, business logic, and data layers
