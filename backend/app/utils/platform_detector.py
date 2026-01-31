from typing import List
from app.models.release_asset import ReleaseAsset # Assuming ReleaseAsset model exists here


def detect_platforms_from_assets(assets: List[ReleaseAsset]) -> List[str]:
    platforms = set()

    for asset in assets:
        name = asset.name.lower()

        if any(x in name for x in ['.exe', '.msi', 'win', 'windows']):
            platforms.add('windows')
        if any(x in name for x in ['.dmg', '.pkg', 'mac', 'darwin', 'macos']):
            platforms.add('mac')
        if any(x in name for x in ['.deb', '.rpm', '.appimage', 'linux']):
            platforms.add('linux')
        if any(x in name for x in ['.apk', 'android']):
            platforms.add('android')

    return list(platforms)
