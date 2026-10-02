from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class OpportunityAnalysis(BaseModel):
    why_it_matters: str = Field(..., description="1-2 sentences on why this is significant")
    business_opportunity: str = Field(..., description="Actionable business idea or opportunity this sparks")
    market_gap: str = Field(..., description="The underlying market gap or emerging customer need")
    affected_players: List[str] = Field(default_factory=list, description="Key companies, industries, or sectors affected")
    tags: List[str] = Field(default_factory=list, description="Industry and topic tags (e.g., #FinTech, #AI, #SaaS)")
    signal_score: float = Field(..., ge=1.0, le=10.0, description="Relevance and actionability score from 1.0 to 10.0")
    key_takeaway: str = Field(..., description="A crisp executive takeaway")

class Article(BaseModel):
    id: str
    title: str
    url: str
    source_name: str
    source_category: str  # Startups & Funding, AI & Tech, Business & Finance, India & MSME
    published_at: Optional[str] = None
    summary: str
    author: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    analysis: Optional[OpportunityAnalysis] = None
    is_saved: bool = False
    is_read: bool = False
    user_notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class VaultItem(BaseModel):
    article_id: str
    notes: Optional[str] = None
    saved_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class DailyBriefing(BaseModel):
    date: str
    top_signals: List[Article]
    opportunity_radar: List[Dict[str, Any]]
    market_gaps: List[Dict[str, str]]
    summary_of_day: str

class CustomAnalysisRequest(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None

class ConfigUpdateRequest(BaseModel):
    gemini_api_key: Optional[str] = None

class MarkReadRequest(BaseModel):
    is_read: bool = True
