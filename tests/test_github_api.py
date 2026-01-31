import json
import os
import sys
from pathlib import Path

# Add the 'backend' directory to the Python path to resolve imports like 'from app.core...'
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.clients.github_client import github_client
from app.core.config import settings
from app.db.session import SessionLocal
from app import crud

# --- Configuration ---
# Create the output directory if it doesn't exist
# The script is run from the root, so the path is relative to the root
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Example repository for testing
TEST_REPO_OWNER = "psf"
TEST_REPO_NAME = "requests"

# --- Helper Function ---
def save_response(filename: str, data: dict):
    """Saves the API response data to a JSON file."""
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Successfully saved response to '{filepath}'")


def run_api_tests():
    """
    Runs a series of requests to the GitHub API via the github_client
    and saves the responses to the '/data' directory.
    """
    print("🚀 Starting GitHub API response analysis script...")
    print("-" * 40)

    # Check if GitHub token is configured
    if not settings.GITHUB_TOKEN or "your_github_token" in settings.GITHUB_TOKEN or "ghp_xxxxx" in settings.GITHUB_TOKEN:
        print("⚠️ WARNING: GitHub token is not configured in 'backend/.env'.")
        print("API requests will be severely rate-limited or fail.")
        print("-" * 40)

    api_calls = [
        {
            "name": "1. Search Repositories",
            "filename": "search_repositories.json",
            "func": lambda: github_client.search_repositories(
                query="language:python stars:>10000", per_page=5
            ),
        },
        {
            "name": "2. Get Repository Details",
            "filename": "get_repository.json",
            "func": lambda: github_client.get_repository(
                owner=TEST_REPO_OWNER, repo=TEST_REPO_NAME
            ),
        },
        {
            "name": "3. List Releases",
            "filename": "list_releases.json",
            "func": lambda: github_client.list_releases(
                owner=TEST_REPO_OWNER, repo=TEST_REPO_NAME
            ),
        },
        {
            "name": "4. Get Latest Release",
            "filename": "get_latest_release.json",
            "func": lambda: github_client.get_latest_release(
                owner=TEST_REPO_OWNER, repo=TEST_REPO_NAME
            ),
        },
        {
            "name": "5. Get README",
            "filename": "get_readme.json",
            "func": lambda: github_client.get_readme(
                owner=TEST_REPO_OWNER, repo=TEST_REPO_NAME
            ),
        },
        {
            "name": "6. Get Rate Limit Status",
            "filename": "get_rate_limit.json",
            "func": lambda: github_client.get_rate_limit(),
        },
        {
            "name": "7. Get Authenticated User",
            "filename": "get_authenticated_user.json",
            "func": lambda: github_client.get_authenticated_user(),
        },
    ]

    for call in api_calls:
        print(f"🔄 Executing: {call['name']}...")
        try:
            response_data = call["func"]()
            save_response(call["filename"], response_data)
        except Exception as e:
            print(f"❌ Error calling '{call['name']}': {e}")
        print("-" * 40)
    
    # Test CRUD methods after API calls
    test_crud_methods()

    print("🎉 Script finished.")
    print(f"All response files are located in the '{DATA_DIR.absolute()}' directory.")

def test_crud_methods():
    """
    Tests additional CRUD methods that don't call the GitHub API directly.
    """
    print("🔬 Testing additional CRUD methods...")
    print("-" * 40)
    db = SessionLocal()
    try:
        print("🔄 Testing get_all_topics...")
        topics = crud.repository.get_all_topics(db, limit=10)
        if topics:
            print(f"✅ Success! Found {len(topics)} topics. Top topic: '{topics[0].topic}' with count {topics[0].count}")
        else:
            print("⚠️ get_all_topics returned no results, but the call succeeded.")
    except Exception as e:
        print(f"❌ Error testing get_all_topics: {e}")
    finally:
        db.close()
    print("-" * 40)

if __name__ == "__main__":
    run_api_tests()