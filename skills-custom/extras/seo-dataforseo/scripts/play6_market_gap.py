"""
Play 6 - Market Gap Finder

Find the best content/affiliate gaps in any niche.
Surfaces clusters where: competition is weak (low DR top 3), affiliate signals exist,
ad density is high (commercial intent), and volume is real.

Usage:
    from play6_market_gap import market_gap_finder
    result = market_gap_finder("bathroom accessories")
    result = market_gap_finder("cannabis dispensary", location_name="Minnesota")
"""
import sys
import json
import math
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))

from api.labs import get_keyword_ideas, get_search_intent, get_bulk_keyword_difficulty
from api.serp import get_google_serp
from api.backlinks import get_bulk_backlinks_summary
from core.storage import save_result
from config.settings import settings

# Domains that signal an affiliate-friendly SERP
AFFILIATE_SIGNAL_DOMAINS = [
    "amazon.com", "target.com", "walmart.com", "wayfair.com", "overstock.com",
    "bestbuy.com", "homedepot.com", "lowes.com", "rakuten.com", "shareasale.com",
    "nerdwallet.com", "thespruce.com", "goodhousekeeping.com", "bhg.com",
    "bobvila.com", "architecturaldigest.com", "housebeautiful.com",
]

# Aggregators/directories that signal easy-to-beat competition
WEAK_COMPETITION = [
    "yelp.com", "yellowpages.com", "angieslist.com", "thumbtack.com",
    "wikipedia.org", "reddit.com", "quora.com", "answers.com",
]

# Gap scoring weights
W_VOLUME        = 0.30
W_CPC           = 0.25
W_LOW_KD        = 0.20
W_AFFILIATE_SIG = 0.15
W_WEAK_COMP     = 0.10


def _gap_score(vol: int, cpc: float, kd: int,
               has_affiliate: bool, has_weak_comp: bool) -> float:
    """Composite score 0-100 for gap opportunity quality."""
    vol_norm   = min(math.log10(max(vol, 10)) / 5, 1.0)       # log-scale volume
    cpc_norm   = min(cpc / 10.0, 1.0)                          # cap at $10 CPC
    kd_norm    = max(0, (60 - kd) / 60)                        # inverse KD (lower = better)
    aff_bonus  = 1.0 if has_affiliate else 0.0
    weak_bonus = 1.0 if has_weak_comp else 0.0

    score = (
        vol_norm   * W_VOLUME +
        cpc_norm   * W_CPC +
        kd_norm    * W_LOW_KD +
        aff_bonus  * W_AFFILIATE_SIG +
        weak_bonus * W_WEAK_COMP
    ) * 100

    return round(score, 1)


def _check_serp_signals(keyword: str, location_name: str) -> Dict:
    """Quick SERP check for affiliate/weak-competition signals."""
    try:
        serp = get_google_serp(keyword, location_name=location_name, depth=10)
        if not serp:
            return {"has_affiliate": False, "has_weak_comp": False, "top3_domains": [], "avg_dr": None}

        items = serp.get("items", []) or []
        top3_domains = []
        has_affiliate = False
        has_weak_comp = False
        ad_count = 0

        for item in items:
            item_type = item.get("type", "")
            domain = urlparse(item.get("url", "")).netloc.replace("www.", "")

            if item_type == "organic" and item.get("rank_absolute", 99) <= 3:
                top3_domains.append(domain)
                if any(sig in domain for sig in AFFILIATE_SIGNAL_DOMAINS):
                    has_affiliate = True
                if any(weak in domain for weak in WEAK_COMPETITION):
                    has_weak_comp = True

            if item_type == "paid":
                ad_count += 1

        return {
            "has_affiliate":   has_affiliate,
            "has_weak_comp":   has_weak_comp,
            "top3_domains":    top3_domains[:3],
            "ad_count":        ad_count,
            "high_intent":     ad_count >= 2,
        }
    except Exception:
        return {"has_affiliate": False, "has_weak_comp": False, "top3_domains": [], "avg_dr": None}


def market_gap_finder(
    niche: str,
    min_volume: int = 300,
    max_kd: int = 50,
    min_cpc: float = 0.0,
    location_name: str = "United States",
    check_serps: bool = True,
    keyword_limit: int = 200,
) -> Dict[str, Any]:
    """
    Find the best gap opportunities in a niche.

    Args:
        niche: Topic/niche to research (e.g. "bathroom decor", "vegan restaurants Minneapolis")
        min_volume: Minimum monthly search volume (default 300)
        max_kd: Maximum keyword difficulty (default 50)
        min_cpc: Minimum CPC to include (default 0 = include all)
        location_name: Target location
        check_serps: Pull live SERPs for top candidates to check affiliate/competition signals
        keyword_limit: How many keywords to pull from Labs (default 200, max 1000)

    Returns:
        Dict with gap_opportunities list sorted by gap_score, plus cluster summaries
    """
    settings.validate()

    print(f"Market Gap Finder — '{niche}'")
    print(f"Pulling {keyword_limit} keyword ideas...")

    # Step 1: Get keyword ideas
    raw_ideas = get_keyword_ideas(niche, limit=keyword_limit) or []
    print(f"  Got {len(raw_ideas)} keyword ideas")

    # Step 2: Filter and enrich with difficulty
    candidates = []
    keywords_for_difficulty = []

    for item in raw_ideas:
        vol = item.get("search_volume", 0) or 0
        cpc = item.get("cpc", 0.0) or 0.0
        kw  = item.get("keyword", "")
        if vol >= min_volume and cpc >= min_cpc and kw:
            candidates.append({"keyword": kw, "volume": vol, "cpc": cpc, "kd": None})
            keywords_for_difficulty.append(kw)

    print(f"  {len(candidates)} passed volume/CPC filters")

    if not candidates:
        return {"status": "no_results", "niche": niche, "message": "No keywords passed filters"}

    # Step 3: Get keyword difficulty in bulk
    try:
        kd_results = get_bulk_keyword_difficulty(keywords_for_difficulty[:1000]) or []
        kd_map = {}
        for item in kd_results:
            kd_map[item.get("keyword", "")] = item.get("keyword_difficulty", 50) or 50
        for c in candidates:
            c["kd"] = kd_map.get(c["keyword"], 50)
    except Exception as e:
        print(f"  KD lookup failed: {e} — using default KD=50")
        for c in candidates:
            c["kd"] = 50

    # Filter by KD
    candidates = [c for c in candidates if c["kd"] <= max_kd]
    print(f"  {len(candidates)} passed KD≤{max_kd} filter")

    # Step 4: Check SERPs for top candidates (most expensive part)
    serp_checked = 0
    if check_serps:
        # Sort by raw opportunity first, check top 30
        candidates.sort(key=lambda x: (x["volume"] * x["cpc"]) / max(x["kd"], 1), reverse=True)
        to_check = candidates[:30]
        print(f"  Checking SERPs for top {len(to_check)} candidates...")
        for c in to_check:
            signals = _check_serp_signals(c["keyword"], location_name)
            c.update(signals)
            serp_checked += 1

    # Fill in defaults for unscanned keywords
    for c in candidates:
        if "has_affiliate" not in c:
            c.update({"has_affiliate": False, "has_weak_comp": False,
                       "top3_domains": [], "ad_count": 0, "high_intent": False})

    # Step 5: Score and classify gaps
    for c in candidates:
        c["gap_score"] = _gap_score(
            c["volume"], c["cpc"], c["kd"],
            c["has_affiliate"], c["has_weak_comp"]
        )
        # Classify gap type
        if c["has_affiliate"] and c["cpc"] >= 1.0:
            c["gap_type"] = "affiliate"
        elif c["has_weak_comp"]:
            c["gap_type"] = "easy_rank"
        elif c["high_intent"]:
            c["gap_type"] = "high_intent"
        elif c["volume"] >= 1000:
            c["gap_type"] = "volume_play"
        else:
            c["gap_type"] = "long_tail"

    candidates.sort(key=lambda x: x["gap_score"], reverse=True)

    # Top 50 gaps
    top_gaps = candidates[:50]

    # Cluster by gap type
    clusters = {}
    for c in top_gaps:
        gt = c["gap_type"]
        if gt not in clusters:
            clusters[gt] = []
        clusters[gt].append(c)

    result = {
        "status": "success",
        "niche": niche,
        "total_keywords_analyzed": len(raw_ideas),
        "qualified_gaps": len(candidates),
        "serp_checked": serp_checked,
        "top_gaps": top_gaps,
        "clusters": clusters,
        "affiliate_count":    sum(1 for c in top_gaps if c["gap_type"] == "affiliate"),
        "easy_rank_count":    sum(1 for c in top_gaps if c["gap_type"] == "easy_rank"),
        "high_intent_count":  sum(1 for c in top_gaps if c["gap_type"] == "high_intent"),
        "timestamp": datetime.now().isoformat(),
    }

    save_result(result, category="labs", operation="market_gap", keyword=niche)

    # Print summary
    print(f"\n{'='*60}")
    print(f"MARKET GAP FINDER — '{niche}'")
    print(f"{'='*60}")
    print(f"Keywords analyzed:  {len(raw_ideas)}")
    print(f"Qualified gaps:     {len(candidates)}")
    print(f"Affiliate plays:    {result['affiliate_count']}")
    print(f"Easy ranks:         {result['easy_rank_count']}")
    print(f"High intent:        {result['high_intent_count']}")
    print()
    print("TOP 20 GAPS:")
    for gap in top_gaps[:20]:
        aff = "💰" if gap["gap_type"] == "affiliate" else \
              "🎯" if gap["gap_type"] == "easy_rank" else \
              "🔥" if gap["gap_type"] == "high_intent" else "📊"
        print(f"  {aff} [{gap['gap_score']:.0f}] {gap['keyword']}")
        print(f"     vol={gap['volume']:,} cpc=${gap['cpc']:.2f} kd={gap['kd']}")

    return result
