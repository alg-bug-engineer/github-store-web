# GitHub Releases Store

A web application to discover, browse, and download open-source applications from GitHub Releases.

## Project Structure

```
github-store-web/
├── backend/          # FastAPI backend
├── frontend/         # Vue.js frontend
├── docs/             # Documentation
├── docker-compose.yml
└── github-releases-store.html  # MVP prototype
```

## Prerequisites

- Python 3.10+
- Node.js 20.19+ or 22.12+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

## Quick Start

### 1. Start Dependencies

```bash
docker-compose up -d
```

This starts PostgreSQL (port 5432) and Redis (port 6379).

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings (GitHub token, Kimi API key, etc.)

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at http://localhost:8000

API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at http://localhost:5173

## Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_SERVER` | PostgreSQL host | localhost |
| `POSTGRES_USER` | Database user | postgres |
| `POSTGRES_PASSWORD` | Database password | postgres |
| `POSTGRES_DB` | Database name | github_store |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `GITHUB_TOKEN` | GitHub API token | - |
| `KIMI_API_KEY` | Kimi AI API key | - |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | localhost:3000,5173 |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register user |
| `/api/v1/auth/login` | POST | Login user |
| `/api/v1/discover/home` | GET | Home recommendations |
| `/api/v1/discover/hot` | GET | Hot repositories |
| `/api/v1/discover/new` | GET | New discoveries |
| `/api/v1/repositories/{owner}/{repo}` | GET | Repository details |
| `/api/v1/favorites` | GET/POST | User favorites |
| `/api/v1/ai/chat` | POST | AI assistant |

## Data Sync

### Initial Data Sync (Required)

After setting up the database, you need to sync data from GitHub:

```bash
cd backend

# Sync popular repositories and their releases
python scripts/sync_data.py

# Sync only pre-defined popular repos (faster)
python scripts/sync_data.py --popular-only

# Sync with a custom limit per category
python scripts/sync_data.py --limit 10
```

This will:
1. Fetch repository information from GitHub
2. Sync release versions and changelog
3. Sync downloadable assets (APK, EXE, DMG, etc.)

### Automatic Sync with Celery

For continuous background syncing:

```bash
cd backend
celery -A app.worker worker --loglevel=info
```

This runs hourly sync tasks automatically.

## Development

### Build Frontend for Production

```bash
cd frontend
npm run build
```

### API Testing

Visit http://localhost:8000/docs for Swagger UI to test all API endpoints.

## Troubleshooting

### CSS Not Working
Ensure Tailwind CSS v4 is properly configured. The project uses `@tailwindcss/vite` plugin.

### CORS Errors
Check that `BACKEND_CORS_ORIGINS` includes the frontend URL (default: http://localhost:5173).

### Database Connection Issues
Verify PostgreSQL is running: `docker-compose ps`

### No Backend Logs
Check terminal running uvicorn. Logs are configured at INFO level.

## License

MIT
