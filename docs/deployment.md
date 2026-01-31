# Deployment and Startup Guide

## Prerequisites
- **Docker & Docker Compose** (used only for the Postgres database because the backend assumes `localhost` in `.env`).
- **Python 3.10** and `pip` for the backend.
- **Node.js 20.19.x or >= 22.12.0** for the frontend.
- **Redis** listening on `localhost:6379` (Celery/async tasks assume a local Redis instance; install and start it manually if you are not running a containerized Redis).
- **Environment file** copied from `backend/.env.example` or use the provided `backend/.env`. Keep the values in sync with the services you start (e.g., `POSTGRES_SERVER` should stay `localhost`).

## Database (Postgres)
1. From the repository root, copy the backend `.env` into the root if you want to use Compose with its variables:
   ```sh
   cp backend/.env .env
   ```
   This ensures `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are available to `docker compose`.
2. Start the Postgres container:
   ```sh
   docker compose up -d db
   ```
3. Apply migrations once the container is healthy:
   ```sh
   cd backend
   python -m alembic upgrade head
   ```
   (If you only need to bootstrap data, `app/db/initial_data.py` can also be executed here.)

## Backend
1. Activate your Python 3.10 virtual environment and install dependencies:
   ```sh
   cd backend
   python -m pip install -r requirements.txt
   ```
2. Ensure `.env` contains values for:
   - `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`
   - `REDIS_HOST`, `REDIS_PORT`
   - `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
   - `GITHUB_TOKEN`, `KIMI_API_KEY`, `KIMI_API_BASE`
3. Start the app server:
   ```sh
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The API will be reachable at `http://localhost:8000/api/v1/`.
4. (Optional) Run the Celery worker for background tasks:
   ```sh
   celery -A app.worker worker --loglevel info
   ```

## Frontend
1. From the repo root:
   ```sh
   cd frontend
   npm install
   ```
2. Start the Vite dev server:
   ```sh
   npm run dev -- --host 0.0.0.0 --port 5173
   ```
   Visit `http://localhost:5173/` and make sure the backend URL is `http://localhost:8000` so CORS matches the allowed origins.

## Notes & Troubleshooting
- **Pydantic warnings** about `orm_mode` vs `from_attributes` are emitted because the project uses Pydantic v1 configuration inside a V2 environment. They are harmless for now but can be resolved by updating model `Config` classes to declare `from_attributes = True`.
- **Postgres connection refused** means the `db` service is not running or is bound to a different host/port. Check `docker compose ps` and make sure you copied the `.env` values before starting the container.
- **Redis** is not containerized in this repository, so start it separately (e.g., `redis-server` on macOS) if Celery is required.
- **Environment consistency**: If you want to run everything from Docker later, you'll need to reconfigure `POSTGRES_SERVER` to the service name (`db`) and wire `redis` into Compose.
