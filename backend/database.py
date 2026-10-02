import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import Article, OpportunityAnalysis, VaultItem

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "news_vault.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Articles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        source_name TEXT NOT NULL,
        source_category TEXT NOT NULL,
        published_at TEXT,
        summary TEXT,
        author TEXT,
        content TEXT,
        image_url TEXT,
        analysis_json TEXT,
        is_saved INTEGER DEFAULT 0,
        is_read INTEGER DEFAULT 0,
        read_at TEXT,
        user_notes TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # Check if is_read or read_at columns exist in existing database
    cursor.execute("PRAGMA table_info(articles)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "is_read" not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN is_read INTEGER DEFAULT 0")
    if "read_at" not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN read_at TEXT")

    # Clean up any old Pune & Maharashtra categorized articles
    cursor.execute("DELETE FROM articles WHERE source_category = 'Pune & Maharashtra'")
    
    # Idea Vault / Bookmarks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS idea_vault (
        article_id TEXT PRIMARY KEY,
        notes TEXT,
        saved_at TEXT NOT NULL,
        FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
    )
    """)
    
    # App Settings (e.g. Gemini API Key)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_article(article: Article):
    conn = get_connection()
    cursor = conn.cursor()
    analysis_str = article.analysis.model_dump_json() if article.analysis else None
    
    cursor.execute("""
    INSERT INTO articles (id, title, url, source_name, source_category, published_at, summary, author, content, image_url, analysis_json, is_saved, is_read, read_at, user_notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(url) DO UPDATE SET
        title=excluded.title,
        summary=excluded.summary,
        analysis_json=COALESCE(articles.analysis_json, excluded.analysis_json)
    """, (
        article.id,
        article.title,
        article.url,
        article.source_name,
        article.source_category,
        article.published_at,
        article.summary,
        article.author,
        article.content,
        article.image_url,
        analysis_str,
        1 if article.is_saved else 0,
        1 if article.is_read else 0,
        datetime.now().isoformat() if article.is_read else None,
        article.user_notes,
        article.created_at
    ))
    conn.commit()
    conn.close()

def mark_article_read(article_id: str, is_read: bool = True) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat() if is_read else None
    cursor.execute("UPDATE articles SET is_read = ?, read_at = ? WHERE id = ?", (1 if is_read else 0, now_iso, article_id))
    conn.commit()
    conn.close()
    return is_read

def get_articles(
    category: Optional[str] = None, 
    search: Optional[str] = None, 
    unread_only: bool = False,
    history_only: bool = False,
    limit: int = 100,
    offset: int = 0
) -> List[Article]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT a.*, v.notes as vault_notes, CASE WHEN v.article_id IS NOT NULL THEN 1 ELSE 0 END as in_vault
    FROM articles a
    LEFT JOIN idea_vault v ON a.id = v.article_id
    WHERE 1=1
    """
    params = []
    
    if category and category != "All" and category != "Vault" and category != "History":
        query += " AND a.source_category = ?"
        params.append(category)
        
    if category == "Vault":
        query += " AND v.article_id IS NOT NULL"

    if category == "History" or history_only:
        query += " AND a.is_read = 1"

    if unread_only and not history_only and category != "History":
        query += " AND a.is_read = 0"
        
    if search:
        query += " AND (a.title LIKE ? OR a.summary LIKE ? OR a.analysis_json LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
        
    if category == "History" or history_only:
        query += " ORDER BY COALESCE(a.read_at, a.created_at) DESC LIMIT ? OFFSET ?"
    else:
        query += " ORDER BY a.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    articles = []
    for r in rows:
        analysis_obj = None
        if r["analysis_json"]:
            try:
                data = json.loads(r["analysis_json"])
                analysis_obj = OpportunityAnalysis(**data)
            except Exception:
                analysis_obj = None
                
        articles.append(Article(
            id=r["id"],
            title=r["title"],
            url=r["url"],
            source_name=r["source_name"],
            source_category=r["source_category"],
            published_at=r["published_at"],
            summary=r["summary"],
            author=r["author"],
            content=r["content"],
            image_url=r["image_url"],
            analysis=analysis_obj,
            is_saved=bool(r["in_vault"]),
            is_read=bool(r["is_read"]),
            user_notes=r["vault_notes"] or r["user_notes"],
            created_at=r["created_at"]
        ))
        
    conn.close()
    return articles

def get_articles_count(
    category: Optional[str] = None, 
    search: Optional[str] = None, 
    unread_only: bool = False,
    history_only: bool = False
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT COUNT(*) as total
    FROM articles a
    LEFT JOIN idea_vault v ON a.id = v.article_id
    WHERE 1=1
    """
    params = []
    
    if category and category != "All" and category != "Vault" and category != "History":
        query += " AND a.source_category = ?"
        params.append(category)
        
    if category == "Vault":
        query += " AND v.article_id IS NOT NULL"

    if category == "History" or history_only:
        query += " AND a.is_read = 1"

    if unread_only and not history_only and category != "History":
        query += " AND a.is_read = 0"
        
    if search:
        query += " AND (a.title LIKE ? OR a.summary LIKE ? OR a.analysis_json LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])

    cursor.execute(query, params)
    r = cursor.fetchone()
    count = r["total"] if r else 0
    conn.close()
    return count

def get_unread_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as unread FROM articles WHERE is_read = 0")
    r = cursor.fetchone()
    count = r["unread"] if r else 0
    conn.close()
    return count

def get_history_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as history_count FROM articles WHERE is_read = 1")
    r = cursor.fetchone()
    count = r["history_count"] if r else 0
    conn.close()
    return count

def get_reading_history(limit: int = 30) -> List[Article]:
    return get_articles(history_only=True, limit=limit)

def get_article_by_id(article_id: str) -> Optional[Article]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, v.notes as vault_notes, CASE WHEN v.article_id IS NOT NULL THEN 1 ELSE 0 END as in_vault
    FROM articles a
    LEFT JOIN idea_vault v ON a.id = v.article_id
    WHERE a.id = ?
    """, (article_id,))
    r = cursor.fetchone()
    conn.close()
    
    if not r:
        return None
        
    analysis_obj = None
    if r["analysis_json"]:
        try:
            analysis_obj = OpportunityAnalysis(**json.loads(r["analysis_json"]))
        except Exception:
            pass
            
    return Article(
        id=r["id"],
        title=r["title"],
        url=r["url"],
        source_name=r["source_name"],
        source_category=r["source_category"],
        published_at=r["published_at"],
        summary=r["summary"],
        author=r["author"],
        content=r["content"],
        image_url=r["image_url"],
        analysis=analysis_obj,
        is_saved=bool(r["in_vault"]),
        is_read=bool(r["is_read"]),
        user_notes=r["vault_notes"] or r["user_notes"],
        created_at=r["created_at"]
    )

def toggle_vault(article_id: str, notes: Optional[str] = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT article_id FROM idea_vault WHERE article_id = ?", (article_id,))
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute("DELETE FROM idea_vault WHERE article_id = ?", (article_id,))
        cursor.execute("UPDATE articles SET is_saved = 0, user_notes = NULL WHERE id = ?", (article_id,))
        is_saved = False
    else:
        now = datetime.now().isoformat()
        cursor.execute("INSERT INTO idea_vault (article_id, notes, saved_at) VALUES (?, ?, ?)", (article_id, notes, now))
        cursor.execute("UPDATE articles SET is_saved = 1, user_notes = ? WHERE id = ?", (notes, article_id))
        is_saved = True
        
    conn.commit()
    conn.close()
    return is_saved

def save_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_setting(key: str) -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    r = cursor.fetchone()
    conn.close()
    return r["value"] if r else None
