import asyncio
import hashlib
import feedparser
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import urllib.request
import re

from .models import Article
from .sources import FEEDS, SEED_ARTICLES
from .database import save_article, get_articles
from .analyzer import is_noise, analyze_article

def is_english_text(text: str) -> bool:
    if not text:
        return False
    # Check for Devanagari, Arabic, Cyrillic, Chinese, etc.
    if re.search(r'[\u0900-\u097F\u0A80-\u0AFF\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F\u0600-\u06FF\u0400-\u04FF\u4E00-\u9FFF]', text):
        return False
    # Check that at least 80% of alphabetic characters are standard Latin ASCII
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return True
    ascii_letters = [c for c in letters if ord(c) < 128]
    return (len(ascii_letters) / len(letters)) >= 0.85

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text(separator=" ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_image_url(entry: Any) -> Optional[str]:
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']
                
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            if 'url' in thumb:
                return thumb['url']
                
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href') or enc.get('url')
                
    content_html = ""
    if hasattr(entry, 'summary'):
        content_html += entry.summary
    if hasattr(entry, 'content') and entry.content:
        for c in entry.content:
            content_html += c.value
            
    if content_html:
        soup = BeautifulSoup(content_html, "html.parser")
        img = soup.find('img')
        if img and img.get('src'):
            src = img['src']
            if src.startswith('http'):
                return src
                
    return None

def fetch_single_feed(feed_info: Dict[str, Any]) -> List[Article]:
    articles = []
    feed_url = feed_info["url"]
    feed_name = feed_info["name"]
    category = feed_info["category"]
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(feed_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()
            parsed = feedparser.parse(content)
    except Exception as e:
        print(f"Error fetching {feed_name} ({feed_url}): {e}")
        try:
            parsed = feedparser.parse(feed_url)
        except Exception:
            return []

    for entry in parsed.entries[:10]:
        try:
            title = entry.get('title', '').strip()
            link = entry.get('link', '').strip()
            
            if not title or not link:
                continue
                
            raw_summary = entry.get('summary', '') or entry.get('description', '')
            summary = clean_html(raw_summary)
            if len(summary) > 400:
                summary = summary[:400] + "..."
                
            # STRICT FILTER: English Only!
            if not is_english_text(title) or not is_english_text(summary):
                continue

            # Noise Filter
            if is_noise(title, summary):
                continue
                
            image_url = extract_image_url(entry)
            
            pub_date = entry.get('published', '') or entry.get('updated', '')
            if not pub_date:
                pub_date = datetime.now().strftime("%b %d, %Y")
                
            article_id = hashlib.md5(link.encode('utf-8')).hexdigest()
            analysis = analyze_article(title, summary, category)
            
            article = Article(
                id=article_id,
                title=title,
                url=link,
                source_name=feed_name,
                source_category=category,
                published_at=pub_date,
                summary=summary,
                author=entry.get('author', None),
                image_url=image_url,
                analysis=analysis
            )
            articles.append(article)
        except Exception as err:
            print(f"Error parsing entry in {feed_name}: {err}")
            continue

    return articles

async def sync_all_feeds() -> int:
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, fetch_single_feed, feed) for feed in FEEDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_saved = 0
    for res in results:
        if isinstance(res, list):
            for article in res:
                save_article(article)
                total_saved += 1
                
    return total_saved

def init_seed_data_if_needed():
    existing = get_articles(limit=5)
    if not existing:
        print("Populating initial English high-signal seed intelligence...")
        for s in SEED_ARTICLES:
            art = Article(**s)
            save_article(art)
