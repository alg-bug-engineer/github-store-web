from app.models.repository import Repository


CATEGORY_KEYWORDS = {
    'productivity': ['productivity', 'office', 'notes', 'todo', 'calendar'],
    'developer_tools': ['developer', 'ide', 'editor', 'terminal', 'git', 'code'],
    'media': ['video', 'audio', 'music', 'player', 'streaming', 'media'],
    'utilities': ['utility', 'tool', 'system', 'monitor', 'cleaner'],
    'games': ['game', 'gaming', 'emulator'],
    'security': ['security', 'password', 'vpn', 'encryption', 'privacy'],
    'education': ['education', 'learning', 'tutorial', 'course'],
}


def detect_category(repo: Repository) -> str:
    text = f"{repo.name} {repo.description or ''} {' '.join(repo.topics or [])}".lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category

    return 'other'
