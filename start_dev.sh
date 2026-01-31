#!/bin/bash
#
# Local Development Setup Script
# This script is DESTRUCTIVE and will wipe the local dev database.
#

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
COMPOSE_FILE="docker-compose.yml"

# --- Main Logic ---

echo "--- Setting up Local Development Environment ---"

# 1. Stop and remove dev database containers and volumes
echo "🛑 Stopping and removing existing dev database and redis..."
docker-compose -f "$COMPOSE_FILE" down -v
echo "✅ Dev services and data wiped."

# 2. Start fresh database and redis services
echo "🚀 Starting new database and redis services in Docker..."
docker-compose -f "$COMPOSE_FILE" up -d
echo "⏳ Waiting for database to be ready..."
sleep 10 # Give the database time to initialize
echo "✅ Database and redis are running."

# 3. Set up Backend
echo "🐍 Setting up backend..."
cd backend

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing backend dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Reset database, run migrations, and sync data
echo "🗃️  Resetting database..."
echo 'y' | python scripts/reset_db.py
echo "Applying backend migrations..."
alembic upgrade head
echo "🔄 Running initial data sync..."
python scripts/sync_data.py

echo "✅ Backend setup complete."
cd ..

# 4. Set up Frontend
echo "🌐 Setting up frontend..."
cd frontend
echo "Installing frontend dependencies..."
npm install > /dev/null 2>&1
echo "✅ Frontend setup complete."
cd ..


# 5. Final Instructions
echo ""
echo "🎉 --- Local Development Environment is Ready! --- 🎉"
echo ""
echo "To start the servers, please open TWO separate terminals:"
echo ""
echo "In Terminal 1, run the BACKEND server:"
echo "---------------------------------------"
echo "cd backend"
echo "source venv/bin/activate"
echo "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "---------------------------------------"
echo ""
echo "In Terminal 2, run the FRONTEND server:"
echo "---------------------------------------"
echo "cd frontend"
echo "npm run dev"
echo "---------------------------------------"
echo ""
