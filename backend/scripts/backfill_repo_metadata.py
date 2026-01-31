import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add the project root to the sys.path to allow imports from app
# Assumes script is in backend/scripts/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.db.session import SessionLocal
from app.models.repository import Repository
from app.models.release import Release
from app.models.release_asset import ReleaseAsset
from app.crud.release import release as crud_release
from app.crud.release_asset import release_asset as crud_release_asset
from app.utils.platform_detector import detect_platforms_from_assets
from app.utils.category_detector import detect_category


def backfill_repository_metadata():
    db: Session = SessionLocal()
    try:
        repos = db.query(Repository).all()
        for repo in repos:
            print(f"Processing repository: {repo.full_name}")

            # Get latest release
            latest_release = crud_release.get_latest_release_by_repo_id(db, repo_id=repo.id)
            if latest_release:
                repo.latest_version = latest_release.tag_name
                repo.latest_release_date = latest_release.published_at

                # Detect platforms
                assets = crud_release_asset.get_multi_by_release_id(db, release_id=latest_release.id)
                repo.detected_platforms = detect_platforms_from_assets(assets)
                print(f"  - Detected platforms: {repo.detected_platforms}")
            else:
                repo.latest_version = None
                repo.latest_release_date = None
                repo.detected_platforms = []
                print("  - No releases found for this repository.")

            # Detect category
            repo.primary_category = detect_category(repo)
            print(f"  - Detected category: {repo.primary_category}")
            
            # Recalculate total_downloads by summing downloads from all assets for all releases of this repo
            all_assets_for_repo = []
            all_releases = crud_release.get_multi_by_repo_id(db, repo_id=repo.id, limit=None) # Get all releases
            for rel in all_releases:
                all_assets_for_repo.extend(crud_release_asset.get_multi_by_release_id(db, release_id=rel.id, limit=None))
            
            repo.total_downloads = sum(asset.download_count for asset in all_assets_for_repo if asset.download_count is not None)
            print(f"  - Total downloads: {repo.total_downloads}")

            db.add(repo) # Add the modified repository back to the session
        
        db.commit()
        print("Data backfill completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred during backfill: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    backfill_repository_metadata()
