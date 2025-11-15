# Live Demo  
https://fulfil-io-3.onrender.com

# Product Importer

A scalable web application for importing products from CSV files into a SQL database, built with FastAPI, PostgreSQL, and Celery.

## Features

- **File Upload**: Upload CSV files up to 500K records with real-time progress tracking
- **Product Management**: Full CRUD operations with search, filtering, and pagination
- **Bulk Operations**: Delete all products with confirmation
- **Webhook Management**: Configure and test webhooks for events
- **Async Processing**: Handle large imports without blocking the UI
- **Duplicate Handling**: Automatic SKU-based deduplication (case-insensitive)

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Queue**: Celery with Redis
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Docker, Render.com ready

## Local Development

### Using Docker Compose (Recommended)

```bash
# Clone and navigate to project
git clone <repository-url>
cd product-importer

# Start all services
docker-compose up --build

# Access the application
open http://localhost:8000
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis
# Update DATABASE_URL and REDIS_URL in models.py and tasks.py

# Start Celery worker
celery -A tasks worker --loglevel=info

# Start FastAPI server
uvicorn main:app --reload

# Access the application
open http://localhost:8000
```

## Deployment

### Render.com (Recommended)

1. Push code to GitHub
2. Connect repository to Render
3. Use the provided `render.yaml` configuration
4. Deploy automatically with PostgreSQL and Redis

### Heroku

```bash
# Install Heroku CLI and login
heroku create your-app-name

# Add PostgreSQL and Redis addons
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# Deploy
git push heroku main

# Scale worker
heroku ps:scale worker=1
```

## API Endpoints

- `GET /` - Main upload interface
- `POST /upload` - Upload CSV file
- `GET /task/{task_id}` - Check import progress
- `GET /products` - Product management interface
- `POST /products` - Create product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product
- `DELETE /products` - Delete all products
- `GET /webhooks` - Webhook management
- `POST /webhooks` - Create webhook
- `DELETE /webhooks/{id}` - Delete webhook
- `POST /webhooks/{id}/test` - Test webhook

## CSV Format

```csv
name,sku,description
Product Name,unique-sku-123,Product description here
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

## Performance Notes

- Handles 500K+ records efficiently using Celery background tasks
- Real-time progress updates via polling
- Optimized database operations with bulk inserts
- Pagination for large product lists
- Async webhook processing

## Testing

Upload the included `sample_products.csv` to test the import functionality.
