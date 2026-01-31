from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, func, asc
from pydantic import BaseModel

from app import crud
from app.api import deps
from app.schemas.user_favorite import UserFavorite, UserFavoriteCreate, UserFavoriteWithRepo
from app.schemas.repository import Repository
from app.models.user import User
from app.models.repository import Repository as ModelRepository
from app.models.user_favorite import UserFavorite as ModelUserFavorite


router = APIRouter()


class FavoriteCheckResponse(BaseModel):
    is_favorited: bool


class FavoriteListResponse(BaseModel):
    items: List[UserFavoriteWithRepo]
    total: int


class FavoriteAddRequest(BaseModel):
    repo_id: int
    note: Optional[str] = None


@router.post("/", response_model=UserFavorite)
def create_favorite(
    *,
    db: Session = Depends(deps.get_db),
    request: FavoriteAddRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new user favorite.
    """
    favorite = crud.user_favorite.get_by_user_id_and_repo_id(
        db, user_id=current_user.id, repo_id=request.repo_id
    )
    if favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repository already favorited by this user.",
        )

    # Check if repository exists
    repository = crud.repository.get(db, id=request.repo_id)
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found.",
        )

    obj_in = UserFavoriteCreate(
        user_id=current_user.id, repo_id=request.repo_id, note=request.note
    )
    favorite = crud.user_favorite.create(db, obj_in=obj_in)
    return favorite


@router.delete("/{repo_id}", response_model=UserFavorite)
def delete_favorite(
    *,
    db: Session = Depends(deps.get_db),
    repo_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a user favorite.
    """
    favorite = crud.user_favorite.get_by_user_id_and_repo_id(
        db, user_id=current_user.id, repo_id=repo_id
    )
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found for this user and repository.",
        )
    favorite = crud.user_favorite.remove(db, id=favorite.id)
    return favorite


@router.get("/", response_model=FavoriteListResponse)
def read_favorites(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort: Optional[str] = Query(None, description="Sort by: stars, updated, created, favorited_at"),
    order: Optional[str] = Query("desc", description="Order: asc or desc"),
    language: Optional[str] = Query(None, description="Filter by programming language"),
    platform_type: Optional[str] = Query(None, description="Filter by platform type (e.g., android, desktop, cli, web)"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve user favorites with repository data, with optional filtering and sorting.
    """
    query = db.query(ModelUserFavorite, ModelRepository).join(
        ModelRepository, ModelUserFavorite.repo_id == ModelRepository.id
    ).filter(ModelUserFavorite.user_id == current_user.id)

    # Apply filters
    if language:
        query = query.filter(ModelRepository.language == language)
    
    if platform_type:
        if platform_type == "cli":
            query = query.filter(func.lower(ModelRepository.category).like("%cli%"))
        else:
            query = query.filter(ModelRepository.category == platform_type)

    # Get total count before pagination and full fetch
    total = query.count()

    # Apply sorting
    if sort == "stars":
        if order == "asc":
            query = query.order_by(asc(ModelRepository.stars))
        else:
            query = query.order_by(desc(ModelRepository.stars))
    elif sort == "updated":
        if order == "asc":
            query = query.order_by(asc(ModelRepository.github_updated_at))
        else:
            query = query.order_by(desc(ModelRepository.github_updated_at))
    elif sort == "created":
        if order == "asc":
            query = query.order_by(asc(ModelRepository.github_created_at))
        else:
            query = query.order_by(desc(ModelRepository.github_created_at))
    elif sort == "favorited_at":
        if order == "asc":
            query = query.order_by(asc(ModelUserFavorite.created_at))
        else:
            query = query.order_by(desc(ModelUserFavorite.created_at))
    else: # Default sort by favorited_at desc
        query = query.order_by(desc(ModelUserFavorite.created_at))

    # Apply pagination
    favorites_with_repos = query.offset(skip).limit(limit).all()

    items = []
    for fav, repo in favorites_with_repos:
        items.append(UserFavoriteWithRepo(
            id=fav.id,
            user_id=fav.user_id,
            repo_id=fav.repo_id,
            note=fav.note,
            created_at=fav.created_at,
            repository=Repository.model_validate(repo),
        ))

    return FavoriteListResponse(items=items, total=total)


@router.get("/check/{repo_id}", response_model=FavoriteCheckResponse)
def check_favorite(
    *,
    db: Session = Depends(deps.get_db),
    repo_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Check if a repository is favorited by the current user.
    """
    favorite = crud.user_favorite.get_by_user_id_and_repo_id(
        db, user_id=current_user.id, repo_id=repo_id
    )
    return FavoriteCheckResponse(is_favorited=favorite is not None)
