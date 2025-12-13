# FastDjango

> **The Best of Both Frameworks at your service.**

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern backend template that combines Django's battle-tested ORM with FastAPI's high-performance async capabilities. Perfect for building robust, scalable web APIs with the stability of Django's database layer and the speed of FastAPI's async architecture.

## Features

- **Hybrid Architecture**: Django ORM + FastAPI async endpoints
- **Complete Authentication**: JWT-based auth with registration, login, token refresh, and password management
- **User Profile Management**: Comprehensive user information and profile handling
- **Media Management**: File upload/download with streaming support, thumbnail generation, and multiple storage backends (Local, AWS S3, Google Cloud)
- **Rate Limiting**: Built-in request throttling to protect your API
- **Background Jobs**: APScheduler integration for scheduled tasks
- **Clean Architecture**: Service layer pattern with dependency injection
- **Auto-generated API Docs**: Interactive Swagger UI and ReDoc documentation
- **Production Ready**: Health checks, structured logging, and exception handling

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Anthony-Asamoah/Backend-py-.git
   cd Backend[py]
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   cd src
   python manage.py migrate
   ```

6. **Start the server**
   ```bash
   python start_server.py
   ```

   The API will be available at `http://localhost:8000`

### First API Call

Test the health check endpoint:
```bash
curl http://localhost:8000/api/v1/health
```

## Project Structure

```
src/
├── main/                    # Core application
│   ├── settings.py         # Django settings
│   ├── asgi.py            # Django + FastAPI integration
│   ├── router.py          # Main API router
│   ├── middleware/        # Custom middleware (rate limiting)
│   └── utils/             # Shared utilities
├── auth/                   # Authentication module
│   ├── models.py          # User account models
│   ├── schema.py          # Pydantic schemas
│   ├── api.py             # API endpoints
│   └── use_cases/         # Business logic
├── user_info/             # User profile module
│   ├── models.py          # User info models
│   ├── schema.py          # Pydantic schemas
│   ├── api.py             # API endpoints
│   └── use_cases/         # Business logic
└── media/                 # Media management module
    ├── models.py          # Media models
    ├── schema.py          # Pydantic schemas
    ├── api.py             # API endpoints
    └── use_cases/         # Business logic
```

### Architecture Pattern

Each module follows a clean architecture pattern:
```
models.py → schema.py → use_cases/ → api.py
   ↓           ↓            ↓          ↓
 Django     Pydantic    Business    FastAPI
  ORM      Validation    Logic     Endpoints
```

## API Documentation

FastDjango provides auto-generated, interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

All endpoints, request/response schemas, and authentication requirements are documented automatically.

## Configuration

### Environment Variables

See `.env.example` for all available configuration options. Key settings include:

**Application Settings**
- `APP_TITLE`: Application title (default: "FastDjango")
- `APP_VERSION`: API version
- `APP_HOST`: Server host
- `APP_PORT`: Server port (default: 8000)
- `API_PREFIX`: API route prefix (default: "/api/v1")

**Rate Limiting**
- `RATE_LIMIT`: Maximum requests per time window (default: 10)
- `TIME_WINDOW`: Time window in seconds (default: 3)

**Storage Backends**
- `STORAGE_TYPE`: `LOCAL`, `S3`, or `GCP`
- `MEDIA_ROOT`: Local storage directory
- For S3/GCP: Configure additional cloud credentials in settings

## Architecture Highlights

### Django + FastAPI Integration

FastDjango uniquely combines Django and FastAPI:

1. **Django Setup First**: Django is initialized to make the ORM available
2. **FastAPI for APIs**: All HTTP endpoints use FastAPI for async performance
3. **Shared Settings**: Both frameworks use Django's settings.py
4. **Django Admin Available**: Access Django admin at `/django/admin`

This hybrid approach gives you:
- Django's mature ORM & migrations
- FastAPI's async capabilities, automatic validation, and modern API features
- Best of both ecosystems without compromise

### Service Layer Pattern

Business logic is encapsulated in service classes that inherit from `BaseService`

### Base Model

All models inherit from `BaseModel` which provides:
- `cursor`: Auto-incrementing primary key for cursor pagination
- `id`: UUID for public reference
- `created_on`: Automatic creation timestamp
- `updated_on`: Automatic update timestamp

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application
COPY src/ ./src/
COPY .env .env

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD cd src && python manage.py migrate && python start_server.py
```

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: fastdjango
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_NAME: fastdjango
    volumes:
      - ./src:/app/src
      - media_data:/app/media

volumes:
  postgres_data:
  media_data:
```

Run with Docker:
```bash
docker-compose up -d
```

### Production Considerations

1. **Environment Variables**: Use a secure method to manage secrets (e.g., AWS Secrets Manager, HashiCorp Vault)
2. **Database Migrations**: Run migrations before starting: `python manage.py migrate`
3. **Static Files**: Serve media files with a CDN or object storage (S3/GCS)
4. **Reverse Proxy**: Use Nginx or Traefik for SSL termination and load balancing
5. **Health Checks**: Monitor the `/api/v1/health` endpoint
6. **Logging**: Set `LOG_LEVEL` appropriately (20 for INFO, 10 for DEBUG)

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Development

### Creating a New Module

1. **Create module directory** in `src/`
2. **Define models** in `models.py` (inherit from `BaseModel`)
3. **Create Pydantic schemas** in `schema.py`
4. **Implement use cases** in `use_cases/` directory
5. **Create service class** in `use_cases/__init__.py`
6. **Define API endpoints** in `api.py` using `SafeAPIRouter`
7. **Register router** in `main/router.py`

### Adding New Endpoints

```python
from main.utils.base_classes import SafeAPIRouter

router = SafeAPIRouter(prefix="/your-module", tags=["Your Module"])

@router.get("/items")
async def list_items():
    # Your logic here
    return {"items": []}
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations
```

### Running Tests

```bash
# Add your test framework (e.g., pytest)
pip install pytest pytest-asyncio

# Run tests
pytest
```

## Contributing

We welcome contributions! Here's how you can help:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** to ensure nothing breaks
5. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use type hints where possible
- Write docstrings for public functions and classes
- Keep functions focused and single-purpose
- Use the existing service layer pattern

### Pull Request Process

1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Update the README if needed
5. Request review from maintainers

### Reporting Issues

- Use the issue tracker for bug reports and feature requests
- Provide clear reproduction steps for bugs
- Include environment details (Python version, OS, etc.)

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 FastDjango Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Support

- Documentation: Check `/docs` when running the server
- Issues: Use the GitHub issue tracker
- Discussions: Start a discussion for questions and ideas

---

Built with Django + FastAPI - The best of both frameworks at your service.