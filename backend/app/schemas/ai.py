from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request model for AI chat endpoint"""
    message: str
    conversation_id: Optional[str] = None


class ProjectInfo(BaseModel):
    """Project information returned in chat response"""
    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    url: str
    stars: Optional[int] = None
    avatar_url: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for AI chat endpoint"""
    reply: str
    projects: List[ProjectInfo] = []
    conversation_id: Optional[str] = None
