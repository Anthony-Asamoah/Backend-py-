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
├── main/                  # Core application
│   ├── settings.py        # Django settings
│   ├── asgi.py            # Django + FastAPI integration
│   ├── router.py          # Main API router
│   ├── middleware/        # Custom middleware (rate limiting)
│   └── utils/             # Shared utilities
├── auth/                  # Authentication module
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

FastDjango includes separate Docker Compose configurations for local development and production environments.

#### Local Development with Docker

1. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

2. **Start services**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **View logs**
   ```bash
   docker-compose -f docker-compose.yml logs -f web
   ```

4. **Optional: Start with pgAdmin** (for database management)
   ```bash
   docker-compose -f docker-compose.yml --profile tools up -d
   ```
   pgAdmin will be available at `http://localhost:5050`

**Local Features:**
- Hot reload enabled (code changes reflect immediately)
- Source code mounted as volume
- pgAdmin for database management
- Debug logging enabled

#### Production Deployment with Docker

1. **Configure production environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values:
   # - Set strong DB_PASSWORD
   # - Set secure SECRET_KEY
   # - Set your domain via APP_HOST (e.g., api.yourdomain.com)
   # - Set ACME_EMAIL for Let's Encrypt
   # - Set APP_RELOAD=False
   # - Set LOG_LEVEL=20 (INFO) or 30 (WARNING)
   ```

2. **Start services without Traefik** (if using external reverse proxy)
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Start services with Traefik** (includes automatic SSL)
   ```bash
   docker-compose -f docker-compose.prod.yml --profile traefik up -d
   ```

**Production Features:**
- Multi-stage optimized Dockerfile
- Non-root user for security
- Health checks for all services
- Traefik reverse proxy with automatic SSL (Let's Encrypt)
- Automatic HTTP to HTTPS redirect
- Production logging and restart policies

#### Traefik Configuration

When using Traefik (production), configure these environment variables in `.env`:

```bash
# Your API domain
APP_HOST=api.yourdomain.com

# Email for Let's Encrypt SSL certificates
ACME_EMAIL=admin@yourdomain.com

# Traefik dashboard domain (optional)
TRAEFIK_DOMAIN=traefik.yourdomain.com

# Generate basic auth password:
# htpasswd -nb admin yourpassword
TRAEFIK_BASIC_AUTH=admin:$apr1$...
```

**Traefik Dashboard:** Access at `https://traefik.yourdomain.com` (if configured)

#### Useful Docker Commands

```bash
# View all running containers
docker-compose -f docker-compose.yml ps

# Stop all services
docker-compose -f docker-compose.yml down

# Stop and remove volumes (⚠️ deletes data)
docker-compose -f docker-compose.yml down -v

# Rebuild containers after dependency changes
docker-compose -f docker-compose.yml build --no-cache

# Run Django management commands
docker-compose -f docker-compose.yml exec web python src/manage.py createsuperuser

# Access database
docker-compose -f docker-compose.yml exec db psql -U postgres -d fastdjango
```

### Production Considerations

1. **Environment Variables**:
   - Never commit `.env` to version control
   - Use secure methods for secrets (AWS Secrets Manager, HashiCorp Vault)
   - Rotate credentials regularly

2. **Database Migrations**:
   - Migrations run automatically on container start
   - For zero-downtime deployments, run migrations separately before updating containers

3. **Media Files**:
   - For production at scale, use S3/GCS instead of local storage
   - Set `STORAGE_TYPE=S3` or `STORAGE_TYPE=GCP` in `.env`

4. **SSL/TLS**:
   - Traefik handles SSL automatically with Let's Encrypt
   - Ensure ports 80 and 443 are open
   - DNS must point to your server before starting

5. **Health Checks**:
   - Monitor `/api/v1/health` endpoint
   - Docker health checks configured for all services

6. **Logging**:
   - Use `LOG_LEVEL=20` (INFO) for production
   - Consider centralized logging (ELK, CloudWatch, etc.)

7. **Backups**:
   - Regularly backup PostgreSQL database
   - Backup media files if using local storage

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

@router.get(
   "/items",
    response_model=YourModuleOutSchema,
    status_code=200,
)(your_modeule_service.get)
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: Check `/docs` when running the server
- Issues: Use the GitHub issue tracker
- Discussions: Start a discussion for questions and ideas

---

Built with Django + FastAPI - The best of both frameworks at your service.