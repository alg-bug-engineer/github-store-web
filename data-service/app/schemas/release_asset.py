from pydantic import BaseModel
from typing import Optional


class ReleaseAssetBase(BaseModel):
    release_id: int
    github_asset_id: Optional[int] = None
    name: str
    label: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    browser_download_url: str
    download_count: int = 0
    platform: Optional[str] = None
    file_type: Optional[str] = None


class ReleaseAssetCreate(ReleaseAssetBase):
    pass


class ReleaseAssetUpdate(ReleaseAssetBase):
    pass


class ReleaseAssetInDBBase(ReleaseAssetBase):
    id: int

    class Config:
        from_attributes = True


class ReleaseAsset(ReleaseAssetInDBBase):
    pass


class ReleaseAssetInDB(ReleaseAssetInDBBase):
    pass
