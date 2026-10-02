# The Personal Signal 📰
### *Single-Page Personal Newspaper & Opportunity Discovery Broadsheet*
*Designed with Palette #30 of the Japanese Dictionary of Color Combinations*

**The Personal Signal** is a personal newspaper and opportunity discovery terminal tailored for founders and investors focusing on Startups, AI & Deep Tech, Business & Finance, and India MSME & Commercial Policy.

---

## 🎨 Japanese Color Combinations (Palette #30)

- **Pompeian Red (`#AB2439`)**: Lead headlines, active section ribbons, breaking stamps, unread badges.
- **Mineral Gray (`#A2B0AD`)**: Section dividers, opportunity lens borders, muted tags.
- **Warm Japanese Newsprint Cream (`#F7F2EB`)**: High-contrast, easy-on-the-eyes editorial broadsheet page background.
- **Sumi Charcoal Ink (`#1C1A18`)**: Authentic editorial typography using *Playfair Display* and *Newsreader*.

---

## 🗞️ Broadsheet Experience (Single-Page • Zero Scrolling)

- **Strict Single-Page Fit**: The entire paper fits inside your browser window (`100vh; overflow: hidden;`). No endless vertical scrolling.
- **Newspaper Pagination**: Turn pages just like a physical newspaper using:
  - The bottom pagination controls (`◀ Previous Page` and `Next Page ▶`).
  - **Keyboard Arrow Keys** (`Left Arrow` ◀ and `Right Arrow` ▶) to turn pages instantly.
- **Unread & New Stories Tracking**:
  - Unread counter in the top folio (`● 128 New Signals`).
  - Toggle **"New Only"** switch to only view stories you haven't opened yet.
  - Every unread article features a **"NEW"** stamp and Pompeian Red indicator border.
- **Click to Get the Full Picture**:
  - Clicking any article card opens the **Opportunity & Strategic Lens** modal.
  - Automatically marks the article as **viewed / read** in your local database.
  - Teardown sections:
    - 🎯 *Executive Takeaway*
    - 💡 *Actionable Startup / Business Opportunity*
    - 🔍 *Underlying Market Gap*
    - 🏢 *Affected Companies & Industries*
    - ✍️ *Personal Idea Scratchpad* (record private notes directly to your Idea Vault).

---

## 🚀 Running the Newspaper

The server is currently running at:
👉 **[http://localhost:8000](http://localhost:8000)**

To launch it at any time in the future:
```powershell
python run.py
```

---

## 🏛️ Project Structure

```
d:/AntiGravityProject/ProjectNews/
├── backend/
│   ├── models.py       # Pydantic schemas with is_read and pagination
│   ├── sources.py      # Curated Indian & Global startup/tech feeds
│   ├── database.py     # SQLite persistence with is_read & vault tracking
│   ├── analyzer.py     # Noise filter & Opportunity Discovery Engine
│   ├── fetcher.py      # Concurrency RSS parser
│   └── server.py       # FastAPI REST endpoints & broadsheet server
├── static/
│   ├── index.html      # Broadsheet single-page newspaper layout
│   ├── style.css       # Japanese Palette #30 styling & zero-scroll rules
│   └── app.js          # Page turning, keyboard shortcuts, unread tracking
├── test_app.py         # End-to-end integration test suite
└── run.py              # Server launcher
```
