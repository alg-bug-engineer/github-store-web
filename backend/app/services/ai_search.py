import re
import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_, func, case

from app.models.repository import Repository


logger = logging.getLogger(__name__)


# Chinese and English stopwords to filter out
STOPWORDS = {
    # Chinese
    "的", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看",
    "好", "自己", "这", "那", "什么", "怎么", "可以", "能", "想", "找", "用",
    "个", "工具", "软件", "应用", "程序", "帮", "帮我", "请", "麻烦", "需要",
    "推荐", "有没有", "有什么", "求",
    # English
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
    "us", "them", "my", "your", "his", "its", "our", "their",
    "this", "that", "these", "those", "what", "which", "who", "whom",
    "find", "looking", "for", "want", "tool", "app", "application",
    "recommend", "suggest", "any", "some", "please", "help",
}


def extract_keywords(message: str) -> List[str]:
    """
    Extract search keywords from user message.
    Uses simple tokenization + stopword filtering.
    """
    # Convert to lowercase
    text = message.lower()

    # Extract Chinese and English words
    # Chinese: continuous Chinese characters
    # English: continuous alphanumeric characters
    chinese_pattern = r'[\u4e00-\u9fff]+'
    english_pattern = r'[a-zA-Z0-9]+'

    chinese_words = re.findall(chinese_pattern, message)
    english_words = re.findall(english_pattern, text)

    # For Chinese, split into individual characters and common bigrams
    chinese_tokens = []
    for word in chinese_words:
        # Keep the full word if it's meaningful (2-4 chars)
        if 2 <= len(word) <= 4:
            chinese_tokens.append(word)
        # Also extract bigrams for longer words
        if len(word) > 2:
            for i in range(len(word) - 1):
                bigram = word[i:i+2]
                chinese_tokens.append(bigram)

    all_tokens = chinese_tokens + english_words

    # Filter stopwords and short tokens
    keywords = []
    seen = set()
    for token in all_tokens:
        token_lower = token.lower()
        if (token_lower not in STOPWORDS and
            len(token) >= 2 and
            token_lower not in seen):
            keywords.append(token)
            seen.add(token_lower)

    logger.info(f"Extracted keywords from '{message}': {keywords}")
    return keywords[:5]  # Limit to top 5 keywords


def search_repositories(
    db: Session,
    keywords: List[str],
    limit: int = 5
) -> List[Repository]:
    """
    Search repositories using PostgreSQL ILIKE matching.
    Searches in name, description, and topics fields.
    """
    if not keywords:
        return []

    # Build OR conditions for each keyword
    conditions = []
    for keyword in keywords:
        pattern = f"%{keyword}%"
        conditions.append(Repository.name.ilike(pattern))
        conditions.append(Repository.description.ilike(pattern))
        # For topics array, use ANY
        conditions.append(
            func.array_to_string(Repository.topics, ',').ilike(pattern)
        )

    # Query with relevance scoring
    # Prioritize name matches, then description, then topics
    query = (
        db.query(Repository)
        .filter(Repository.is_active == True)
        .filter(or_(*conditions))
    )

    # Order by: name match priority, then stars
    # Build a case expression for name matches
    name_match_cases = []
    for keyword in keywords:
        name_match_cases.append(
            Repository.name.ilike(f"%{keyword}%")
        )

    # Combine name matches into a single score
    if name_match_cases:
        # Use a case to prioritize exact name matches
        query = query.order_by(
            # Repositories with name matches come first
            case(
                (or_(*name_match_cases), 0),
                else_=1
            ),
            Repository.stars.desc()
        )
    else:
        query = query.order_by(Repository.stars.desc())

    results = query.limit(limit).all()
    logger.info(f"Found {len(results)} repositories for keywords: {keywords}")
    return results


class AISearchService:
    """Service for AI-powered project search and recommendation"""

    def search_projects(
        self,
        db: Session,
        message: str,
        limit: int = 5
    ) -> List[Repository]:
        """
        Search for projects based on user message.
        Extracts keywords and performs database search.
        """
        keywords = extract_keywords(message)
        if not keywords:
            logger.warning(f"No keywords extracted from message: {message}")
            return []

        return search_repositories(db, keywords, limit)

    def format_projects_for_prompt(
        self,
        projects: List[Repository]
    ) -> str:
        """Format projects list for inclusion in AI prompt"""
        if not projects:
            return ""

        lines = []
        for project in projects:
            topics_str = ", ".join(project.topics[:3]) if project.topics else "N/A"
            lines.append(
                f"- 【{project.name}】: {project.description or 'No description'}\n"
                f"  Stars: {project.stars} | 分类: {project.primary_category or project.category or 'Unknown'}"
            )

        return "\n".join(lines)


# Singleton instance
ai_search_service = AISearchService()
