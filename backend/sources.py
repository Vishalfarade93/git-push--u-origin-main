"""
Curated high-signal English RSS feeds and news sources aligned specifically with:
- Startups, business, finance, AI, technology
- India & emerging market trends, new business models, VC funding & investments
- Government policies affecting businesses & MSMEs
Strictly in ENGLISH only.
"""

FEEDS = [
    # Startups & Venture Capital (English)
    {
        "id": "inc42",
        "name": "Inc42",
        "category": "Startups & Funding",
        "url": "https://inc42.com/feed/",
        "weight": 1.2
    },
    {
        "id": "yourstory",
        "name": "YourStory",
        "category": "Startups & Funding",
        "url": "https://yourstory.com/feed",
        "weight": 1.1
    },
    {
        "id": "entrackr",
        "name": "Entrackr",
        "category": "Startups & Funding",
        "url": "https://entrackr.com/feed/",
        "weight": 1.2
    },
    {
        "id": "tc_startups",
        "name": "TechCrunch Startups",
        "category": "Startups & Funding",
        "url": "https://techcrunch.com/category/startups/feed/",
        "weight": 1.0
    },

    # AI & Deep Tech (English)
    {
        "id": "tc_ai",
        "name": "TechCrunch AI",
        "category": "AI & Tech",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "weight": 1.2
    },
    {
        "id": "venturebeat_ai",
        "name": "VentureBeat AI",
        "category": "AI & Tech",
        "url": "https://venturebeat.com/category/ai/feed/",
        "weight": 1.1
    },
    {
        "id": "hackernews",
        "name": "Hacker News Top",
        "category": "AI & Tech",
        "url": "https://news.ycombinator.com/rss",
        "weight": 1.0
    },

    # Business, Finance & Markets (English)
    {
        "id": "livemint_tech",
        "name": "Mint Tech & Startups",
        "category": "Business & Finance",
        "url": "https://www.livemint.com/rss/technology",
        "weight": 1.1
    },
    {
        "id": "livemint_companies",
        "name": "Mint Companies & Markets",
        "category": "Business & Finance",
        "url": "https://www.livemint.com/rss/companies",
        "weight": 1.1
    },
    {
        "id": "et_tech",
        "name": "Economic Times Tech",
        "category": "Business & Finance",
        "url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
        "weight": 1.1
    },

    # Policy, MSMEs & Government Initiatives (English Edition)
    {
        "id": "pib_economy_en",
        "name": "PIB India English (Commerce & Economy)",
        "category": "India & MSME",
        "url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=2", # Lang=2 is English
        "weight": 1.2
    },
    {
        "id": "smestreet_en",
        "name": "SMEStreet MSME News (English)",
        "category": "India & MSME",
        "url": "https://smestreet.in/feed/",
        "weight": 1.2
    }
]

# High-signal seed items in pure English
SEED_ARTICLES = [
    {
        "id": "seed-1",
        "title": "RBI & NPCI Pilot Programmable Offline UPI and Credit Lines for MSME Supply Chain Financing",
        "url": "https://www.livemint.com/technology/rbi-npci-msme-programmable-upi",
        "source_name": "Mint Tech & Startups",
        "source_category": "India & MSME",
        "published_at": "Today, 09:15 AM",
        "summary": "The Reserve Bank of India and NPCI have unveiled technical architecture for purpose-bound, programmable UPI vouchers directly tied to GST invoices. Small vendors can now receive instant liquidity discounted against government and enterprise supply orders.",
        "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&auto=format&fit=crop&q=80",
        "analysis": {
            "why_it_matters": "Solves the chronic 90-120 day working capital delay that cripples millions of Indian MSMEs without requiring collateral or expensive bank overdrafts.",
            "business_opportunity": "Building B2B embedded fintech integrations that plug GST ERP systems (Tally, Zoho) directly into programmable UPI discounting rails.",
            "market_gap": "Small sub-contractors currently resort to informal lenders at 24-36% interest due to lack of real-time verified purchase order financing.",
            "affected_players": ["MSMEs across India", "Tally / Zoho ERPs", "Private Banks", "Fintech Lenders"],
            "tags": ["#FinTech", "#MSME", "#RBI", "#UPI", "#SupplyChain"],
            "signal_score": 9.8,
            "key_takeaway": "Programmable UPI unlocks zero-collateral invoice discounting for millions of Indian small businesses."
        }
    },
    {
        "id": "seed-2",
        "title": "OpenAI & Anthropic Launch Reasoning Agent Frameworks: Indian SaaS Startups Pivot to Autonomous Workflows",
        "url": "https://techcrunch.com/category/artificial-intelligence/",
        "source_name": "TechCrunch AI",
        "source_category": "AI & Tech",
        "published_at": "Today, 07:45 AM",
        "summary": "New multimodal reasoning agents with verifiable tool-calling primitives are triggering a massive rewrite across enterprise vertical software. Founders are moving from chat wrappers to autonomous backend operators.",
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&auto=format&fit=crop&q=80",
        "analysis": {
            "why_it_matters": "The era of shallow GenAI chatbots is ending. True value is migrating to autonomous vertical agents that carry out complex end-to-end multi-step enterprise workflows.",
            "business_opportunity": "Building specialized autonomous agent suites for unsexy enterprise verticals: import/export customs clearance, pharmaceutical drug documentation, and statutory GST reconciliation.",
            "market_gap": "Enterprises don't want another chatbot prompt; they need deterministic, audited software agents that integrate with legacy SAP and Oracle databases.",
            "affected_players": ["Indian IT Services", "SaaS Founders", "Global Enterprise Software"],
            "tags": ["#AI", "#AutonomousAgents", "#SaaS", "#EnterpriseTech"],
            "signal_score": 9.5,
            "key_takeaway": "Autonomous vertical agents are replacing 'copilots'—focus on unglamorous domain-specific backoffice operations."
        }
    },
    {
        "id": "seed-3",
        "title": "Quick Commerce Enters 'Dark Manufacturing': Micro-Factory Hubs for On-Demand Consumer Goods",
        "url": "https://entrackr.com/category/startups/",
        "source_name": "Entrackr",
        "source_category": "Startups & Funding",
        "published_at": "Today, 06:30 AM",
        "summary": "Quick commerce platforms are partnering with local food processing and FMCG micro-units to bake, print, and package fresh consumer goods within 15 minutes of an order, pioneering hyper-localized zero-inventory commerce in tier-1 metro nodes.",
        "image_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&auto=format&fit=crop&q=80",
        "analysis": {
            "why_it_matters": "Shrinks the supply chain to zero days. Eliminates central warehouse warehousing, transit spoilage, and enables customized, on-demand fresh FMCG production.",
            "business_opportunity": "Micro-manufacturing hardware equipment (compact automated packaging, rapid induction baking) tailored for 400-sq-ft urban dark hubs.",
            "market_gap": "Traditional FMCG production equipment is designed for huge 50,000 sq ft rural plants, not modular city micro-kitchens.",
            "affected_players": ["Quick Commerce Platforms", "Legacy FMCG Giants", "Local Artisan Brands"],
            "tags": ["#NewBusinessModels", "#QuickCommerce", "#D2C", "#RetailInnovation"],
            "signal_score": 9.3,
            "key_takeaway": "Micro-manufacturing inside quick-commerce hubs is the next frontier of decentralized retail."
        }
    },
    {
        "id": "seed-4",
        "title": "India Semiconductor Mission Grants 50% Fiscal Support for Advanced Packaging & Compound Semiconductor Units",
        "url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=2",
        "source_name": "PIB India (Commerce & Economy)",
        "source_category": "India & MSME",
        "published_at": "Today, 10:15 AM",
        "summary": "Union Cabinet approved expanding capital expenditure support to include compound semiconductors, OSAT facilities, and precision gas supply suppliers under India's national deep-tech mission.",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
        "analysis": {
            "why_it_matters": "Lowers barriers for domestic hardware suppliers and precision engineering vendors to participate in the global chip fabrication supply chain.",
            "business_opportunity": "Precision cleanroom facility engineering, high-purity chemical distribution, and technical calibration testing services for OSAT plants.",
            "market_gap": "Lack of domestic Tier-2 precision tooling suppliers certified to semiconductor-grade cleanroom tolerances.",
            "affected_players": ["Hardware Startups", "Precision Engineering MSMEs", "Ministry of Electronics & IT"],
            "tags": ["#Semiconductor", "#DeepTech", "#GovernmentSubsidy", "#Manufacturing"],
            "signal_score": 9.6,
            "key_takeaway": "Heavy capital subsidies make precision engineering for hardware supply chains a prime high-margin business."
        }
    },
    {
        "id": "seed-5",
        "title": "Fintech Unicorn Cred Launches Enterprise Treasury Management Platform for High-Growth Startups",
        "url": "https://inc42.com/startups/cred-enterprise-treasury",
        "source_name": "Inc42",
        "source_category": "Startups & Funding",
        "published_at": "Today, 11:30 AM",
        "summary": "Cred has unveiled a specialized liquidity and corporate treasury platform enabling venture-backed startups in India to automate overnight sweep deposits, yield optimization, and vendor disbursements across multi-bank rails.",
        "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&auto=format&fit=crop&q=80",
        "analysis": {
            "why_it_matters": "Startups sitting on $10M-$100M in venture funding often lose 3-5% in annual yield due to idle current accounts and manual treasury management.",
            "business_opportunity": "Automated yield-optimizing corporate accounts and multi-currency treasury SaaS for Indian cross-border exporters and funded startups.",
            "market_gap": "Traditional Indian commercial banks offer archaic net-banking interfaces that require manual physical tokens for every treasury transfer.",
            "affected_players": ["Fintech Startups", "Commercial Banks", "Growth-Stage CFOs"],
            "tags": ["#FinTech", "#TreasurySaaS", "#Startups", "#Capital"],
            "signal_score": 9.4,
            "key_takeaway": "Startup treasury management is opening up as a high-margin B2B fintech battleground."
        }
    }
]
