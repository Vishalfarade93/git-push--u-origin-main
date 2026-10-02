import os
import math
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import requests
from bs4 import BeautifulSoup

from .models import Article, DailyBriefing, CustomAnalysisRequest, ConfigUpdateRequest, MarkReadRequest
from .database import (
    init_db, get_articles, get_articles_count, get_unread_count, get_history_count,
    get_reading_history, mark_article_read, get_article_by_id, toggle_vault, 
    save_setting, get_setting, save_article
)
from .fetcher import sync_all_feeds, init_seed_data_if_needed, clean_html
from .analyzer import analyze_article
from .sources import FEEDS

app = FastAPI(title="The Personal Signal - Personal News & Opportunity Discovery")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and seeds on startup
@app.on_event("startup")
async def on_startup():
    init_db()
    init_seed_data_if_needed()

@app.get("/api/feed")
async def get_feed(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("score"), # "score" or "recent"
    unread_only: bool = Query(False),
    history_only: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=50)
):
    total_count = get_articles_count(category=category, search=search, unread_only=unread_only, history_only=history_only)
    unread_total = get_unread_count()
    history_total = get_history_count()
    
    offset = (page - 1) * per_page
    articles = get_articles(
        category=category, 
        search=search, 
        unread_only=unread_only, 
        history_only=history_only,
        limit=per_page, 
        offset=offset
    )
    
    if not history_only and category != "History":
        if sort == "score":
            articles.sort(key=lambda a: (a.analysis.signal_score if a.analysis else 0), reverse=True)
        else:
            articles.sort(key=lambda a: a.created_at, reverse=True)
        
    total_pages = max(1, math.ceil(total_count / per_page))
    
    return {
        "articles": articles,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "total_count": total_count,
        "unread_count": unread_total,
        "history_count": history_total
    }

@app.get("/api/history")
async def get_history_endpoint(limit: int = Query(30, ge=1, le=100)):
    history_items = get_reading_history(limit=limit)
    return {
        "count": len(history_items),
        "history": history_items
    }

@app.post("/api/articles/{article_id}/read")
async def set_article_read_status(article_id: str, payload: MarkReadRequest):
    status = mark_article_read(article_id, payload.is_read)
    unread_total = get_unread_count()
    history_total = get_history_count()
    return {"article_id": article_id, "is_read": status, "unread_count": unread_total, "history_count": history_total}

@app.post("/api/feed/refresh")
async def refresh_feed(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_all_feeds)
    return {"status": "refreshing", "message": "Synchronizing feeds in the background from active sources"}

@app.get("/api/briefing/today")
async def get_daily_briefing():
    articles = get_articles(limit=40)
    sorted_by_score = sorted(articles, key=lambda a: (a.analysis.signal_score if a.analysis else 0), reverse=True)
    
    top_signals = sorted_by_score[:4]
    
    opportunity_radar = []
    market_gaps = []
    for a in sorted_by_score:
        if a.analysis and a.analysis.business_opportunity:
            opportunity_radar.append({
                "article_id": a.id,
                "title": a.title,
                "category": a.source_category,
                "opportunity": a.analysis.business_opportunity,
                "tags": a.analysis.tags,
                "score": a.analysis.signal_score
            })
            if a.analysis.market_gap:
                market_gaps.append({
                    "topic": a.title[:60] + "...",
                    "gap": a.analysis.market_gap
                })
        if len(opportunity_radar) >= 4:
            break

    today_str = datetime.now().strftime("%A, %B %d, %Y")
    
    return {
        "date": today_str,
        "executive_summary": "High-conviction market signals in Indian industrial automation, programmable MSME credit rails, and generative reasoning agents.",
        "top_signals": top_signals,
        "opportunity_radar": opportunity_radar,
        "market_gaps": market_gaps[:3],
        "total_active_signals": len(articles),
        "unread_count": get_unread_count(),
        "history_count": get_history_count()
    }

@app.post("/api/vault/toggle")
async def toggle_vault_item(payload: Dict[str, Any]):
    article_id = payload.get("article_id")
    notes = payload.get("notes")
    if not article_id:
        raise HTTPException(status_code=400, detail="article_id required")
    
    is_saved = toggle_vault(article_id, notes)
    return {"status": "success", "article_id": article_id, "is_saved": is_saved}

@app.post("/api/vault/notes")
async def update_vault_notes(payload: Dict[str, Any]):
    article_id = payload.get("article_id")
    notes = payload.get("notes", "")
    if not article_id:
        raise HTTPException(status_code=400, detail="article_id required")
        
    import sqlite3
    from .database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE idea_vault SET notes = ? WHERE article_id = ?", (notes, article_id))
    cursor.execute("UPDATE articles SET user_notes = ? WHERE id = ?", (notes, article_id))
    conn.commit()
    conn.close()
    return {"status": "updated", "notes": notes}

@app.post("/api/analyze-custom")
async def analyze_custom(req: CustomAnalysisRequest):
    title = req.title or ""
    summary = req.text or ""
    url = req.url or f"https://custom-input/{hashlib.md5((title + summary).encode()).hexdigest()[:8]}"
    
    if req.url and not summary:
        try:
            resp = requests.get(req.url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
            soup = BeautifulSoup(resp.text, "html.parser")
            if not title:
                title = soup.title.string if soup.title else "Custom Analyzed Article"
            paragraphs = [p.get_text() for p in soup.find_all('p')]
            summary = clean_html(" ".join(paragraphs[:6]))
        except Exception as e:
            if not title:
                title = req.url
            summary = f"Custom link: {req.url}"

    if not title and not summary:
        raise HTTPException(status_code=400, detail="Either URL, Title, or Text must be provided")

    analysis = analyze_article(title, summary, "Startups & Funding")
    article_id = hashlib.md5((url + title).encode()).hexdigest()
    
    article = Article(
        id=article_id,
        title=title,
        url=url,
        source_name="Custom Intelligence Ingestion",
        source_category="Startups & Funding",
        published_at="Just now",
        summary=summary[:400],
        analysis=analysis
    )
    save_article(article)
    return {"status": "analyzed", "article": article}

@app.get("/api/sources")
async def list_sources():
    return {"sources": FEEDS}

@app.get("/api/settings")
async def get_app_settings():
    gemini_key = get_setting("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    return {
        "has_gemini_key": bool(gemini_key),
        "gemini_key_preview": f"••••••••{gemini_key[-4:]}" if gemini_key and len(gemini_key) > 4 else None
    }

@app.post("/api/settings")
async def update_settings(req: ConfigUpdateRequest):
    if req.gemini_api_key is not None:
        save_setting("gemini_api_key", req.gemini_api_key.strip())
    return {"status": "saved", "has_gemini_key": bool(req.gemini_api_key)}

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "The Personal Signal API is operational. Static UI loading..."}
