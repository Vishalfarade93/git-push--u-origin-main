import sqlite3
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

from backend.sources import SEED_ARTICLES
from backend.models import Article
from backend.database import save_article, init_db

init_db()
conn = sqlite3.connect('news_vault.db')
cursor = conn.cursor()

# Remove old seeds or local regional entries
cursor.execute("DELETE FROM articles WHERE id LIKE 'seed-%' OR title LIKE '%Pune%' OR summary LIKE '%Chakan%' OR title LIKE '%Maharashtra%'")
conn.commit()
conn.close()

# Re-insert pure English seeds
for s in SEED_ARTICLES:
    art = Article(**s)
    save_article(art)

print("Database cleaned and initialized with 100% English national and global startup intelligence.")
