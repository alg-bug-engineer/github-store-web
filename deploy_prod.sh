#!/bin/bash
#
# Production Deployment Script
#
# Usage:
#   ./deploy_prod.sh          # Standard deployment (preserves data)
#   ./deploy_prod.sh --fresh  # Fresh deployment (wipes all data)
#

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
FRESH_DEPLOY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fresh)
            FRESH_DEPLOY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./deploy_prod.sh [--fresh]"
            exit 1
            ;;
    esac
done

# --- Main Logic ---

# 1. Check for .env.production file
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: Production environment file '$ENV_FILE' not found."
    echo "Please create it by copying backend/.env.example and filling in the values."
    exit 1
fi

echo "Environment file found."

# 2. Stop services
if [ "$FRESH_DEPLOY" = true ]; then
    echo "FRESH DEPLOYMENT: Stopping and removing all existing services and their data volumes..."
    docker-compose -f "$COMPOSE_FILE" down -v
    echo "Services and data wiped."
else
    echo "STANDARD DEPLOYMENT: Stopping services (preserving data volumes)..."
    docker-compose -f "$COMPOSE_FILE" down
    echo "Services stopped (data preserved)."
fi

# 3. Build and start all services in detached mode
echo "Building new images and starting services..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build
echo "Services are up and running."

# 4. Wait for data-service to be healthy
echo "Waiting for data-service to be healthy..."
sleep 10

# 5. Apply database migrations (via data-service)
echo "Applying database migrations..."
docker-compose -f "$COMPOSE_FILE" exec data-service alembic upgrade head
echo "Migrations applied."

# 6. Fresh deployment: Initialize seed data and run initial sync
if [ "$FRESH_DEPLOY" = true ]; then
    echo "Running initial data sync from GitHub..."
    docker-compose -f "$COMPOSE_FILE" exec data-service python scripts/sync_data.py --popular-only
    echo "Initial data sync complete."
fi

echo ""
echo "--- Deployment Successful! ---"
echo ""
echo "Your application is now deployed and ready."
echo "You can access it at http://localhost (or your server's domain/IP)."
echo ""
echo "Useful commands:"
echo "  - View logs:                docker-compose -f $COMPOSE_FILE logs -f"
echo "  - Check data-service health: curl http://localhost:8001/health"
echo "  - Check migration status:   docker-compose -f $COMPOSE_FILE exec data-service alembic current"
echo "  - Manual data sync:         docker-compose -f $COMPOSE_FILE exec data-service python scripts/sync_data.py"
echo ""
