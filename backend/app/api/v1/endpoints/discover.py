from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from collections import Counter

from app import crud, schemas, models
from app.api import deps
from app.crud.repository import repository as crud_repository
from app.crud.recommendation import recommendation as crud_recommendation
from app.crud.user_favorite import user_favorite as crud_user_favorite
from app.schemas.repository import Repository as SchemaRepository
from app.models.user import User
from app.models.repository import Repository as ModelRepository


router = APIRouter()


@router.get("/home", response_model=Dict[str, Any])
def get_home_recommendations(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get homepage recommendations including hot, new, and editor's choice.
    """
    response = {}

    # Hot Recommendations (based on stars)
    hot_repos = crud_repository.get_multi(db, sort_by="stars", order_by_desc=True, limit=10)
    response["hot"] = [SchemaRepository.model_validate(repo) for repo in hot_repos]

    # New Discoveries (recently added/synced)
    new_repos = crud_repository.get_multi(db, sort_by="created_at", order_by_desc=True, limit=10)
    response["new"] = [SchemaRepository.model_validate(repo) for repo in new_repos]

    # Editor's Choice (from `recommendations` table with type 'editor_choice')
    editor_choice_recs = crud_recommendation.get_by_type(db, type="editor_choice")
    editor_choice_repo_ids = []
    for rec in editor_choice_recs:
        if rec.repo_ids:
            editor_choice_repo_ids.extend(rec.repo_ids)

    editor_choice_repos = []
    if editor_choice_repo_ids:
        editor_choice_repos = crud_repository.get_multi_by_ids(db, ids=editor_choice_repo_ids)
    response["editor_choice"] = [SchemaRepository.model_validate(repo) for repo in editor_choice_repos]

    return response


@router.get("/hot", response_model=List[SchemaRepository])
def get_hot_recommendations(
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=100),
) -> Any:
    """
    Get hot repositories (e.g., based on stars).
    """
    repos = crud_repository.get_multi(db, sort_by="stars", order_by_desc=True, limit=limit)
    return repos


@router.get("/new", response_model=List[SchemaRepository])
def get_new_discoveries(
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=100),
) -> Any:
    """
    Get newly discovered repositories.
    """
    repos = crud_repository.get_multi(db, sort_by="created_at", order_by_desc=True, limit=limit)
    return repos


@router.get("/category/{category}", response_model=List[SchemaRepository])
def get_category_recommendations(
    category: str,
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=100),
) -> Any:
    """
    Get repositories for a specific category.
    """
    repos = db.query(ModelRepository).filter(ModelRepository.category == category).order_by(desc(ModelRepository.stars)).limit(limit).all()
    return repos


@router.get("/personalized", response_model=List[SchemaRepository])
def get_personalized_recommendations(
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get personalized recommendations based on user favorites.
    """
    favorites = crud_user_favorite.get_multi_by_user_id(db, user_id=current_user.id)
    if not favorites:
        # If no favorites, return hot recommendations as a fallback
        return crud_repository.get_multi(db, sort_by="stars", order_by_desc=True, limit=limit)

    preferred_categories = Counter()
    preferred_languages = Counter()

    for fav in favorites:
        repo = crud_repository.get(db, id=fav.repo_id)
        if repo:
            if repo.category:
                preferred_categories[repo.category] += 1
            if repo.language:
                preferred_languages[repo.language] += 1

    recommendations_query = db.query(ModelRepository).filter(
        ModelRepository.is_active == True,
        ModelRepository.has_releases == True,
    )

    if preferred_categories:
        most_common_category = preferred_categories.most_common(1)[0][0]
        recommendations_query = recommendations_query.filter(
            ModelRepository.category == most_common_category
        )
    
    if preferred_languages:
        most_common_language = preferred_languages.most_common(1)[0][0]
        recommendations_query = recommendations_query.filter(
            ModelRepository.language == most_common_language
        )
    
    # Exclude already favorited repositories
    favorited_repo_ids = [fav.repo_id for fav in favorites]
    recommendations_query = recommendations_query.filter(
        ModelRepository.id.notin_(favorited_repo_ids)
    )

    recommendations = recommendations_query.order_by(desc(ModelRepository.stars)).limit(limit).all()

    if not recommendations and preferred_categories:
        # Fallback to broader category search if specific language yields no results
        recommendations_query = db.query(ModelRepository).filter(
            ModelRepository.is_active == True,
            ModelRepository.has_releases == True,
            ModelRepository.category == preferred_categories.most_common(1)[0][0],
            ModelRepository.id.notin_(favorited_repo_ids)
        ).order_by(desc(ModelRepository.stars)).limit(limit).all()
        recommendations = recommendations_query

    if not recommendations:
        # Final fallback to general hot recommendations
        recommendations = crud_repository.get_multi(db, sort_by="stars", order_by_desc=True, limit=limit)

    return recommendations
