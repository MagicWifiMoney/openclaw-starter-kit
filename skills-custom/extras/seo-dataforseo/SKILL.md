---
name: seo-dataforseo
description: "Full-stack SEO intelligence and web scraping via DataForSEO API. 10 plays covering: affiliate keyword mining (any affiliate or content site), competitor teardowns, content calendar building, SERP feature sniping (PAA/featured snippets), local business scraping (churches, dispensaries, restaurants, any category), local pack competitive analysis, expired domain finding (PBN/domain hunting), backlink gap finding, market gap analysis, and bulk domain BVS scoring for outreach. Also classic keyword research, rank tracking, OnPage audits, YouTube gap finding, and trend watching. Use when: researching keywords, analyzing competitors, scraping local businesses, finding link opportunities, building content plans, discovering affiliate plays, or vetting domains. Requires DataForSEO credentials in ~/.env."
---

# DataForSEO — Full Intelligence Stack

Credentials auto-load from `~/.env` (`DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`).
No setup needed — just `cd` to the skill dir and run.

```bash
cd ~/clawd/skills/seo-dataforseo
pip install -r scripts/requirements.txt   # first time only
```

---

## Quick Reference

| You says | Function | Play |
|-----------|----------|------|
| "Find affiliate keywords for [topic]" | `affiliate_keyword_miner("topic")` | 1 |
| "Build a content calendar for [site/niche]" | `content_calendar("yourblog.com")` | 2 |
| "Find PAA questions / featured snippets for [topic]" | `serp_feature_sniper("topic")` | 3 |
| "Tear down [competitor.com]" | `competitor_teardown("topcompetitor.com", your_domain="yourblog.com")` | 4 |
| "Find backlinks they have that I don't" | `backlink_gap_finder("yourblog.com", "topcompetitor.com")` | 5 |
| "Find gaps in [niche]" | `market_gap_finder("bathroom decor")` | 6 |
| "Scrape all [business type] in [state/cities]" | `local_business_scraper("church", state="Minnesota")` | 7 |
| "Who's winning local search for [keyword] in [city]?" | `local_pack_intel("dispensary", "Minneapolis MN")` | 8 |
| "Find expired domains in [niche]" | `expired_domain_finder("home decor blog")` | 9 |
| "Score this list of domains for outreach" | `bvs_score_domains("leads.csv")` | 10 |
| "Research keywords for [topic]" | `keyword_research("topic")` | classic |
| "Check rankings for [domain]" | `rank_check("yourblog.com", ["closet organizer"])` | util |
| "Audit [site] for technical SEO" | `onpage_audit("yourblog.com")` | util |
| "What's trending in [niche]?" | `trend_watch(["bathroom decor", "home organization"])` | util |
| "Find YouTube video gaps for [topic]" | `youtube_gap_finder("bathroom organization")` | util |

---

## Run any play

```python
import sys
sys.path.insert(0, "scripts")
from main import *

# Play 1 - Affiliate keywords for Fifti
result = affiliate_keyword_miner("bathroom decor", cpc_floor=1.0, kd_ceiling=40)

# Play 4 - Tear down a competitor
result = competitor_teardown("topcompetitor.com", your_domain="yourblog.com")

# Play 7 - Scrape local businesses
result = local_business_scraper("dispensary", state="Minnesota")

# Play 9 - Find expired domains
result = expired_domain_finder("home decor blog", dr_floor=15)
```

Or run standalone play scripts directly:
```bash
python3 scripts/play1_affiliate_kw.py
python3 scripts/play7_local_scraper.py
```

---

## The 10 Plays

---

### Play 1 — Affiliate Keyword Miner
**For:** Fifti Fifti, Dog Bathroom Art, any affiliate site
**Finds:** Keywords worth writing content for — high CPC, real affiliate presence, manageable KD

```python
result = affiliate_keyword_miner(
    "bathroom organization",
    cpc_floor=1.0,      # min $1 CPC (signals commercial intent)
    kd_ceiling=40,      # max keyword difficulty
    location_name="United States"
)
```

**What it does:**
1. Labs `keyword_ideas` — 200+ related keywords from your seed
2. Filters: volume ≥ 100, CPC ≥ floor, KD ≤ ceiling
3. Checks organic SERP for affiliate signals (Amazon/Rakuten/ShareASale in top 10 = proven play)
4. Pulls Trends for seasonality peaks
5. Scores each keyword: `affiliate_score = volume × CPC / KD`

**Output:** Ranked keyword list with affiliate_score, cpc, volume, kd, affiliate_signal flag, best months

**Estimated cost:** ~$0.10-0.50 per run (Labs + SERP checks on top candidates)

**Sweet spots for Fifti:**
- "best [product] for small bathroom" (commercial, high CPC, product-focused)
- "[adjective] [room] organization ideas" (informational with affiliate links)
- "how to organize [space]" + strong image pack = content + affiliate hybrid

---

### Play 2 — Content Calendar Builder
**For:** Any site — gives you 3 months of content with target keywords per post

```python
result = content_calendar(
    "yourblog.com",      # or a niche like "bathroom decor tips"
    months=3,
    posts_per_month=8
)
```

**What it does:**
1. If domain given: Labs `keywords_for_site` → what you already rank for → find adjacencies
2. Labs `keyword_ideas` → expand seed keywords into 500+ related terms
3. Clusters by topic/intent (informational / commercial / navigational)
4. Trends → assign seasonal spikes to correct months (don't write "spring cleaning" in November)
5. Prioritizes by `volume × CPC ÷ KD` → highest-value topics go first

**Output:** Month-by-month markdown calendar: post title, target keyword, intent, volume, CPC

**Estimated cost:** ~$0.20-0.50 per run

**Sites to run this for:** yourblog.com, yoursite.com, yourlocal.com, yourniche.com, yoursite.com

---

### Play 3 — SERP Feature Sniper
**For:** Finding PAA questions, featured snippet gaps, image pack opportunities
**Best for:** Fifti (home org = PAA-heavy SERPs), DBA (lots of image packs)

```python
result = serp_feature_sniper(
    "bathroom organization tips",   # or list of keywords
    expand_keywords=True            # auto-find related keywords to scan
)
```

**What it does:**
1. Expands seed to 15+ related keywords (Labs)
2. Pulls SERP for each — extracts: PAA questions, featured snippet holder, image packs, video carousels
3. DR-checks the current feature holders (low DR holder = easy to steal)
4. Scores winnability: high (weak holder or aggregator), medium (moderate DR), low (strong brand)

**Output:** List of PAA questions you can answer + featured snippet opportunities with current holder's DR

**Estimated cost:** ~$0.05-0.15 per run (SERP calls only)

**Play:** If a Wikipedia or Reddit page holds a featured snippet → write a better direct answer → you can steal it

---

### Play 4 — Competitor Teardown
**For:** Full competitive intelligence — what are they ranking for, what drives their traffic, who links to them

```python
result = competitor_teardown(
    "topcompetitor.com",
    your_domain="yourblog.com"   # optional — subtracts your rankings for gap list
)
```

**What it does:**
1. Labs `keywords_for_site` → all keywords they rank for (up to 1,000)
2. Labs `domain_pages` → their top traffic pages (what's actually making them money)
3. Backlinks `summary` → their DR, referring domains, backlink count, spam score
4. If your domain given: subtract your rankings → keyword gap list

**Output:** Markdown report: top keywords, top pages, backlink profile, content gap vs your site

**Estimated cost:** ~$0.05-0.15 per teardown

**Best competitor targets per site:**
- Fifti: topcompetitor.com, competitor2.com, competitor3.com, competitor4.com
- DBA: rover.com, petmd.com, topcompetitor.com/pets
- MPLS Vegan: happycow.net, yelp.com/search Minneapolis
- MN Cannabis: leafly.com, weedmaps.com
- Sermon Clips: sermoncentral.com, preaching.com

---

### Play 5 — Backlink Gap Finder
**For:** Link building — find sites that link to your competitor but not you

```python
result = backlink_gap_finder(
    "yourblog.com",
    "topcompetitor.com",
    min_dr=15    # only include domains with DR ≥ 15
)
```

**What it does:**
1. Backlinks `referring_domains` for competitor (up to 500 domains)
2. Backlinks `referring_domains` for your site
3. Set diff: comp - yours = gap list
4. Filters by min DR, sorts by DR descending

**Output:** Gap domains sorted by DR, marked high/medium/low priority, overlap list, unique-to-you list

**Estimated cost:** ~$0.04 per run (2 backlinks calls)

**The play:** Email the gap domains: "Hey, you linked to The Spruce on bathroom organization — we have a more specific guide at yourblog.com/bathroom-organization, would you consider adding it?"

---

### Play 6 — Market Gap Finder
**For:** Finding the best content/affiliate opportunities in any niche. The "find leverage" play.

```python
result = market_gap_finder(
    "bathroom accessories",
    min_volume=300,
    max_kd=50,
    min_cpc=0.50,          # require some commercial intent
    check_serps=True       # pull live SERPs to check affiliate/competition signals
)
```

**What it does:**
1. Labs `keyword_ideas` → 200+ keywords in the niche
2. `bulk_keyword_difficulty` → KD for all candidates
3. Filters: volume ≥ min, KD ≤ max, CPC ≥ min
4. Checks top-30 SERPs: affiliate signals (Amazon in top 10?), weak competition (Reddit/Quora in top 3?), ad density (high ads = high commercial intent)
5. Scores by composite gap score: `volume × CPC × (1/KD) × affiliate_bonus × weak_comp_bonus`
6. Classifies: affiliate play / easy rank / high intent / volume play / long tail

**Output:** Top 50 gaps ranked by score, clustered by type (affiliate, easy_rank, high_intent)

**Estimated cost:** ~$0.15-0.40 per run

**Recurring uses:**
- Run on "bathroom decor", "kitchen organization", "home storage" for Fifti content pipeline
- Run on "dog decor", "pet bathroom", "dog gifts" for DBA
- Run on "vegan Minneapolis", "plant-based restaurants" for MPLS Vegan
- Run on "Minnesota dispensary", "cannabis near me" for MN Cannabis

---

### Play 7 — Local Business Scraper
**For:** Scraping any category of local businesses across any geography
**The generalized church pipeline — works for any niche**

```python
result = local_business_scraper(
    "church",
    state="Minnesota"         # scrapes all major cities in state
)

result = local_business_scraper(
    "vegan restaurant",
    cities=["Minneapolis MN", "St Paul MN", "Duluth MN"]
)

result = local_business_scraper(
    "cannabis dispensary",
    state="Minnesota",
    output_csv="dispensaries-mn.csv"
)
```

**What it does:**
1. Takes business type + geography (state → auto-expands to major cities, or explicit city list)
2. Google Maps SERP for each city × keyword combo
3. Deduplicates by `place_id` + `website`
4. Extracts: name, website, phone, address, rating, reviews_count, place_id

**Output:** Deduplicated CSV ready for BVS scoring (Play 10) or outreach

**Cost:** $0.002/request × ~100 cities × 3 keyword variants = ~$0.60 for a full state

**Use cases:**
- Church leads for yoursite.com backlinks (already proven — 28k+ churches scraped)
- Dispensaries for MN Cannabis directory expansion
- Vegan restaurants for MPLS Vegan listings
- Dog groomers / pet stores for DBA affiliate outreach
- Any local business category for client lead gen

---

### Play 8 — Local Pack Intel
**For:** Understanding who's winning local search and where the gaps are

```python
result = local_pack_intel(
    "vegan restaurant",
    "Minneapolis MN",
    your_domain="yourlocal.com"    # optional — checks if you appear
)
```

**What it does:**
1. Google Maps SERP → extracts full 3-pack + extended results
2. For each business: rating, review count, website presence, phone, hours
3. Flags weaknesses: no website, few reviews, low rating, no phone, no hours
4. Organic SERP check for local organic rankings
5. If your domain provided: finds your position (or tells you you're missing)

**Output:** 3-pack breakdown with competitor stats, market averages, weakness flags, your position

**Cost:** ~$0.004 per run (1 Maps SERP + 1 Organic SERP)

**The play:** Businesses with "no website" + high reviews = citation opportunity (add them to your directory, they'll link back). Businesses with "few reviews" = weak 3-pack position = you can outrank them with fresh content + GMB optimization.

---

### Play 9 — Expired Domain Finder
**For:** Finding dropped domains with real backlink equity in any niche
**Future feature candidate for Search Console Tools**

```python
result = expired_domain_finder(
    "home decor blog",
    dr_floor=10,        # minimum domain rank
    max_spam=25,        # reject spammy profiles
    location_name="United States"
)
```

**What it does:**
1. Organic SERP for 10+ niche keywords → collect all ranking domains
2. Labs `historical_rank_overview` → confirms which domains actually had sustained rankings (not one-time flukes)
3. Backlinks `summary` → DR, referring domains, spam score for candidates
4. Scores and ranks: DR × log(referring_domains) × (1 - spam/100)
5. Flags: likely expired (recently dropped in rankings + low activity signals)

**Output:** CSV of expired domain candidates with DR, RD, spam score, historical rank data, opportunity score

**Cost:** ~$0.20-0.60 per run (SERP + Labs historical + Backlinks bulk)

**The play:** Redirect expired domain → instant authority transfer. Register → build PBN link. Buy + 301 → pass juice to your money site. At $0.002/SERP and $0.02/backlinks check, this replaces $99/mo Ahrefs expired domain feature.

---

### Play 10 — Bulk BVS Scorer
**For:** Scoring any list of domains for outreach or acquisition value
**Generalized from the church lead scoring pipeline**

```python
result = bvs_score_domains(
    "church-leads.csv",          # CSV with domain/website column
    target_site="yoursite.com"  # optional — used for relevance scoring
)
```

**What it does:**
1. HTTP enrichment for each domain: SSL, has blog, has contact form, has newsletter, has social presence, has staff page, mobile-friendly
2. Backlinks `summary` → DR, referring domains, spam score
3. Scores across 4 pillars:
   - **P1 Link Value (40pts):** DR + referring domains
   - **P2 Opportunity (30pts):** has blog + contact form + no existing link
   - **P3 Reachability (20pts):** has email + staff page + social
   - **P4 Activity (10pts):** recent posts + social activity
4. Tiers: Gold ≥70, Silver ≥50, Bronze ≥30, Skip <30

**Output:** Enriched CSV sorted by BVS score with tier; separate gold/silver CSVs for outreach

**Cost:** $0.02/domain for backlinks data + ~$0.005 for HTTP scraping = ~$40 for 2,000 domains

---

## Always-On Utilities

### Rank Tracker
```python
result = rank_check(
    "yourblog.com",
    ["closet organizer", "bathroom organization ideas", "small bathroom storage"],
    location_name="United States"
)
```
Checks your current position for any keyword list. Run weekly to track progress.
**Cost:** ~$0.002/keyword

### OnPage Audit
```python
result = onpage_audit("yourblog.com")
```
Technical SEO: broken links, missing meta, slow pages, crawl issues, Core Web Vitals signals.
**Cost:** ~$0.000125/page (500-page site ≈ $0.06)

### YouTube Gap Finder
```python
result = youtube_gap_finder("bathroom organization")
```
Finds video content gaps in a niche — what search intent has no good YouTube answer.
**Cost:** ~$0.002-0.01

### Trend Watcher
```python
result = trend_watch(
    ["bathroom decor", "home organization", "closet ideas"],
    location_name="United States"
)
```
Seasonal trends — know when to publish "spring cleaning" content (February, not March).
**Cost:** ~$0.001/5-keyword batch

### Classic Keyword Research
```python
result = keyword_research("closet organizer")          # deep dive, one keyword
result = full_keyword_analysis(["kw1", "kw2", "kw3"]) # multi-keyword analysis
result = competitor_analysis("topcompetitor.com")           # what do they rank for
```

---

## Pricing Reference (accurate as of Feb 2026)

| API | Cost | Notes |
|-----|------|-------|
| Google Maps SERP | $0.002/request | 100 results per call |
| Google Organic SERP | $0.002/10 results | live mode |
| Backlinks summary/live | $0.02/domain | + $0.00003/row |
| Backlinks referring_domains | $0.02/call + $0.00003/row | up to 1,000 rows |
| Labs keyword_ideas | ~$0.01/task + $0.0001/item | |
| Labs keywords_for_site | ~$0.01/task + $0.0001/item | |
| Labs historical_rank | $0.10/task + $0.001/item per domain-month | most expensive Labs endpoint |
| Labs search_intent | $0.001/task + $0.0001/keyword | |
| Google Ads search volume | ~$0.0003-0.001/keyword | varies by endpoint |
| Clickstream bulk volume | $0.01/task + $0.0001/item | best for bulk — ~$110/1M keywords |
| Trends | $0.001/task | 5 keywords per task |
| OnPage basic | $0.000125/page | JS rendering: 10x more expensive |

**Rough play costs:**
- Affiliate keyword miner (200 keywords): ~$0.20-0.50
- Content calendar (1 site, 3 months): ~$0.30-0.80
- Competitor teardown (1 competitor): ~$0.05-0.15
- Local state scrape (1 state, 1 category): ~$0.60-1.50
- Expired domain finder (1 niche): ~$0.30-0.80
- BVS score 2,000 domains: ~$40-45

---

## You's Sites — Suggested Plays

### Fifti Fifti (yourblog.com)
```python
affiliate_keyword_miner("bathroom organization")         # monthly
affiliate_keyword_miner("home storage solutions")
affiliate_keyword_miner("kitchen organization ideas")
content_calendar("yourblog.com", months=3)            # quarterly
serp_feature_sniper("closet organization tips")          # quarterly
competitor_teardown("topcompetitor.com", "yourblog.com")  # one-time + quarterly
backlink_gap_finder("yourblog.com", "topcompetitor.com")  # quarterly
market_gap_finder("bathroom decor", min_cpc=1.0)         # monthly
```

### Dog Bathroom Art (yoursite.com)
```python
affiliate_keyword_miner("dog bathroom decor", cpc_floor=0.50)
affiliate_keyword_miner("pet themed home decor")
market_gap_finder("dog gifts", check_serps=True)
competitor_teardown("chewy.com/blog", "yoursite.com")
serp_feature_sniper("dog bathroom ideas")
```

### MPLS Vegan (yourlocal.com)
```python
local_pack_intel("vegan restaurant", "Minneapolis MN", your_domain="yourlocal.com")
local_pack_intel("plant-based restaurant", "Minneapolis MN")
local_business_scraper("vegan restaurant", state="Minnesota")   # update listings
competitor_teardown("happycow.net", "yourlocal.com")
content_calendar("yourlocal.com", months=3)
```

### MN Cannabis Hub (yourniche.com)
```python
local_pack_intel("cannabis dispensary", "Minneapolis MN")
local_business_scraper("dispensary", state="Minnesota")
market_gap_finder("Minnesota cannabis", location_name="Minnesota")
competitor_teardown("leafly.com", "yourniche.com")
backlink_gap_finder("yourniche.com", "leafly.com")
```

### Sermon Clips (yoursite.com)
```python
bvs_score_domains("churches-v3.csv")                           # score new churches
local_business_scraper("church", state="Texas")                 # expand database
backlink_gap_finder("yoursite.com", "sermoncentral.com")
market_gap_finder("sermon clips online")
```

### Search Console Tools (yoursaas.com)
```python
expired_domain_finder("SEO tools blog", dr_floor=15)           # find domains to acquire
expired_domain_finder("search console tutorial")
market_gap_finder("Google Search Console tools")
competitor_teardown("seoclarity.net", "yoursaas.com")
```

---

## Workflow: Full Site Audit

Run these plays in sequence for any site:

```python
# 1. Where are you now?
rank_check("your-domain.com", ["your", "target", "keywords"])

# 2. Who are you up against?
competitor_teardown("top-competitor.com", your_domain="your-domain.com")

# 3. What links do they have that you don't?
backlink_gap_finder("your-domain.com", "top-competitor.com")

# 4. What content gaps exist?
market_gap_finder("your niche", check_serps=True)

# 5. What SERP features can you win?
serp_feature_sniper("your main topic")

# 6. Build your content plan
content_calendar("your-domain.com", months=3)
```

---

## Results Storage

All results auto-save to `results/` with timestamps:
```
results/
├── keywords_data/     # Search volumes, CPC data
├── labs/              # Keyword ideas, difficulty, competitor data
├── serp/              # SERP results, local pack data
├── serp_features/     # Feature sniper results
├── backlinks/         # Backlink profiles, gap analysis
├── trends/            # Trends data
└── summary/           # Human-readable markdown summaries
```

```python
from main import get_recent_results, load_latest

# See what you've run recently
get_recent_results(limit=10)

# Load most recent gap finder result
data = load_latest("labs", "market_gap")
```

---

## Standalone Play Scripts (run directly from CLI)

Each play has a standalone Python script in `scripts/`:

| Script | CLI Usage |
|--------|-----------|
| `play1_affiliate_kw.py` | `python3 play1_affiliate_kw.py "home organization" 1.0 40` |
| `play2_content_calendar.py` | `python3 play2_content_calendar.py yourblog.com` |
| `play3_serp_sniper.py` | `python3 play3_serp_sniper.py "kw1" "kw2"` or `--domain site.com` |
| `play4_competitor_teardown.py` | `python3 play4_competitor_teardown.py topcompetitor.com yourblog.com` |
| `play5_backlink_gap.py` | `python3 play5_backlink_gap.py yourblog.com topcompetitor.com 20` |
| `play6_market_gap.py` | `python3 play6_market_gap.py yourblog.com overstock.com` |
| `play7_local_scraper.py` | `python3 play7_local_scraper.py "dispensary" "Minneapolis, MN"` |
| `play8_local_pack.py` | `python3 play8_local_pack.py "dog grooming" --city "Minneapolis, MN"` |
| `play9_expired_domains.py` | `python3 play9_expired_domains.py "home decor blog" --dr-floor 15` |
| `play10_bvs_scorer.py` | `python3 play10_bvs_scorer.py leads.csv --target-site yourblog.com` |

All scripts read credentials from `~/.env` (DATAFORSEO_USERNAME / DATAFORSEO_PASSWORD).

### Cost Safeguards

Use `dry_run=True` before any expensive play:
```python
result = market_gap_finder("bathroom decor", dry_run=True)
# Output: "Would check 3 domains. Estimated cost: ~$0.09"

result = backlink_gap_finder("mysite.com", "competitor.com", dry_run=True)
# Output: "Would fetch RDs for 2 domains. Est. cost: ~$0.06"
```

### Quick Cost Reference

| Operation | Unit | Cost |
|-----------|------|------|
| Google Maps SERP | per request | ~$0.002 |
| Google Organic SERP | per 10 results | ~$0.002 |
| Backlinks summary | per domain | ~$0.02 |
| Backlinks referring_domains | per call + $0.00003/row | ~$0.02+ |
| Labs keyword_ideas (200 kws) | per run | ~$0.02 |
| Labs search_intent | per 100 kws | ~$0.01 |
| Trends explore | per keyword | ~$0.005 |
| **Play 1 (affiliate miner)** | per run | $0.10-0.50 |
| **Play 2 (content calendar)** | per run | $0.20-0.50 |
| **Play 3 (SERP sniper, 20 kws)** | per run | $0.08-0.20 |
| **Play 4 (competitor teardown)** | per run | $0.05-0.15 |
| **Play 5 (backlink gap)** | per competitor | $0.04-0.08 |
| **Play 6 (market gap)** | per run | $0.05-0.15 |
| **Play 7 (local scraper, 1 state)** | per run | $0.60-1.50 |
| **Play 8 (local pack, 5 kws)** | per run | $0.02-0.05 |
| **Play 9 (expired domains)** | per run | $0.20-0.60 |
| **Play 10 (BVS, 100 domains)** | per run | $2.00-3.00 |
