import os
import re
import json
from typing import Optional, Dict, Any, List
from .models import OpportunityAnalysis
from .database import get_setting

# Noise keywords to reject or deprioritize
NOISE_KEYWORDS = [
    "murder", "assault", "rape", "killed in road", "horoscope", "astrology",
    "zodiac", "box office collection", "celebrity spotted", "wedding photos",
    "viral reel", "cricket match highlights", "toss update", "ipl score",
    "bjp vs congress", "political verbal duel", "mp slams", "mla arrested for brawl"
]

HIGH_VALUE_KEYWORDS = [
    "startup", "fund", "seed", "series a", "series b", "valuation", "invest", "venture",
    "ai", "artificial intelligence", "llm", "agent", "automation", "deeptech",
    "msme", "sme", "rbi", "gst", "subsidy", "incentive", "policy", "cabinet",
    "manufacturing", "semiconductor", "ev", "battery", "export", "market",
    "opportunity", "supply chain", "logistics", "fintech", "saas", "b2b",
    "acquisition", "ipo", "profitability", "ebitda", "revenue"
]

def is_noise(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    for kw in NOISE_KEYWORDS:
        if kw in text:
            # Check if it has strong business context before discarding
            if not any(bw in text for bw in ["startup", "fintech", "market", "policy", "business", "investment"]):
                return True
    return False

def calculate_heuristic_score(title: str, summary: str, category: str) -> float:
    text = (title + " " + summary).lower()
    score = 6.5
    
    # Category base
    if category == "Startups & Funding":
        score += 1.5
    elif category == "AI & Tech":
        score += 1.6
    elif category == "India & MSME":
        score += 1.4
    elif category == "Business & Finance":
        score += 1.2

    # High-value keywords
    matches = sum(1 for kw in HIGH_VALUE_KEYWORDS if kw in text)
    score += min(matches * 0.35, 2.0)
    
    # Funding amounts mention ($M, Cr, Crore)
    if re.search(r'(\$\d+|\d+\s*cr|\d+\s*crore|\d+\s*million)', text):
        score += 0.8
        
    return min(round(score, 1), 9.9)

def heuristic_opportunity_extractor(title: str, summary: str, category: str) -> OpportunityAnalysis:
    text = (title + " " + summary).lower()
    score = calculate_heuristic_score(title, summary, category)
    
    tags = ["#Business"]
    why_it_matters = ""
    opportunity = ""
    market_gap = ""
    affected = []
    
    # 1. Startups & Funding
    if "fund" in text or "raises" in text or "seed" in text or "series" in text or category == "Startups & Funding":
        tags.extend(["#Startups", "#VC", "#Funding"])
        why_it_matters = f"Highlights active investor conviction in {category.lower()} and signals emerging capital allocation toward innovative Indian models."
        opportunity = "Potential for ancillary service providers, supplier partnerships, or adapting their model for underserved niche customer segments."
        market_gap = "Legacy incumbents are unable to move fast enough to satisfy digital-native expectations in this vertical."
        affected = ["Venture Capitalists", "Incumbent Players", "Early Adopters"]
    
    # 2. AI & Frontier Tech
    elif "ai" in text or "intelligence" in text or "model" in text or "tech" in text or category == "AI & Tech":
        tags.extend(["#AI", "#DeepTech", "#Automation"])
        why_it_matters = "Represents a step-change in computational or algorithmic efficiency, reducing human operational bottlenecks."
        opportunity = "Building specialized vertical workflow integrations or domain-specific data fine-tuning on top of these foundational capabilities."
        market_gap = "Enterprises struggle to deploy raw AI models into compliant, mission-critical production workflows."
        affected = ["Tech Founders", "Software Engineers", "Enterprise CIOs"]

    # 3. India Policy, RBI, MSME
    elif "policy" in text or "rbi" in text or "govt" in text or "msme" in text or category == "India & MSME":
        tags.extend(["#Policy", "#MSME", "#IndiaGrowth"])
        why_it_matters = "Regulatory and financial tailwinds create subsidized incentives and lower entry barriers for compliant businesses."
        opportunity = "Providing compliance automation, subsidized credit facilitation, or supply chain modernization for impacted enterprises."
        market_gap = "Small businesses often lack the bandwidth to navigate updated government schemes, leaving massive subsidies unclaimed."
        affected = ["Indian MSMEs", "Banking & NBFC Sector", "Government Regulators"]
        
    else:
        tags.extend(["#EmergingTrend", "#MarketOpportunity"])
        why_it_matters = "Points to evolving market dynamics, shifting consumer preferences, and industrial modernization in India."
        opportunity = "Analyzing the supply chain to spot unserved B2B needs, distribution challenges, or software modernization points."
        market_gap = "Lack of transparent, digitized solutions tailored for modern Indian commercial workflows."
        affected = ["Industry Leaders", "Entrepreneurs", "Consumers"]

    # Refine tags
    if "fintech" in text or "bank" in text or "upi" in text:
        tags.append("#FinTech")
    if "ev" in text or "electric" in text:
        tags.append("#EV")
    if "saas" in text:
        tags.append("#SaaS")

    # Clean duplicates in tags
    tags = list(dict.fromkeys(tags))[:5]
    
    key_takeaway = f"Strategic signal in {category}: actionable opportunity to address {market_gap[:50]}..."

    return OpportunityAnalysis(
        why_it_matters=why_it_matters,
        business_opportunity=opportunity,
        market_gap=market_gap,
        affected_players=affected,
        tags=tags,
        signal_score=score,
        key_takeaway=key_takeaway
    )

def analyze_with_gemini(title: str, summary: str, category: str, api_key: str) -> Optional[OpportunityAnalysis]:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are an elite venture partner, business strategist, and executive intelligence analyst.
Analyze the following news item strictly from an opportunity and business discovery perspective for an entrepreneur and investor based in India (with special interest in Startups, AI, Tech, Business Models, and Policies/MSMEs).

Headline: {title}
Category: {category}
Summary: {summary}

Respond ONLY in valid raw JSON with this exact schema (no markdown fences, no explanation):
{{
    "why_it_matters": "1-2 concise sentences on why this development is significant (no fluff)",
    "business_opportunity": "1-2 actionable business ideas, startup opportunities, or commercial angles this sparks",
    "market_gap": "The underlying market gap or unserved customer need revealed by this news",
    "affected_players": ["Array", "of", "Key", "Companies/Sectors"],
    "tags": ["#Tag1", "#Tag2", "#Tag3"],
    "signal_score": 8.7,
    "key_takeaway": "One sharp executive sentence summarizing the core insight"
}}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        raw_text = response.text.strip()
        # Clean json backticks if any
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        data = json.loads(raw_text.strip())
        return OpportunityAnalysis(**data)
    except Exception as e:
        print(f"Gemini analysis fallback due to: {e}")
        return None

def analyze_article(title: str, summary: str, category: str) -> OpportunityAnalysis:
    # First check if user provided a Gemini API Key in settings or environment
    api_key = get_setting("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    if api_key:
        result = analyze_with_gemini(title, summary, category, api_key)
        if result:
            return result
            
    # Seamless, instant heuristic analysis engine
    return heuristic_opportunity_extractor(title, summary, category)
