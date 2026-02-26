"""
DataForSEO API Toolkit - Main Entry Point

Full-stack SEO intelligence: keyword research, competitor teardowns, local scraping,
backlink analysis, affiliate keyword mining, content calendars, SERP features, and more.
All results are automatically saved to the /results directory with timestamps.

## Quick Start

    from main import *

    # Classic keyword research
    result = keyword_research("python tutorial")

    # 10 Plays (outcome-oriented workflows)
    result = affiliate_keyword_miner("home organization", cpc_floor=1.0, kd_ceiling=40)
    result = competitor_teardown("overstock.com", your_domain="fifti-fifti.net")
    result = local_business_scraper("church", state="Minnesota")
    result = expired_domain_finder("home decor blog", dr_floor=10)
    result = bvs_score_domains("leads.csv")

## All Plays
    play1: affiliate_keyword_miner(topic, cpc_floor, kd_ceiling)
    play2: content_calendar(domain_or_niche, months)
    play3: serp_feature_sniper(topic_or_keywords)
    play4: competitor_teardown(competitor_domain, your_domain)
    play5: backlink_gap_finder(your_domain, competitor_domain)
    play6: market_gap_finder(niche)
    play7: local_business_scraper(business_type, cities, state)
    play8: local_pack_intel(keyword, city)
    play9: expired_domain_finder(niche_keywords, dr_floor, max_spam)
    play10: bvs_score_domains(csv_path, target_site)

## Always-On Utilities
    rank_check(domain, keywords, location)
    onpage_audit(url)
    youtube_gap_finder(topic)
    trend_watch(topics, location)
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import all API modules
from api.keywords_data import (
    get_search_volume,
    get_keywords_for_site,
    get_ad_traffic_by_keywords,
    get_keywords_for_keywords
)
from api.labs import (
    get_keyword_overview,
    get_keyword_suggestions,
    get_keyword_ideas,
    get_related_keywords,
    get_bulk_keyword_difficulty,
    get_historical_search_volume,
    get_search_intent,
    get_domain_keywords,
    get_competitors,
    get_keywords_for_site as get_labs_keywords_for_site
)
from api.serp import (
    get_google_serp,
    get_youtube_serp,
    get_google_maps_serp,
    get_google_news_serp,
    get_google_images_serp,
    get_featured_snippet
)
from api.trends import (
    get_trends_explore,
    get_youtube_trends,
    get_news_trends,
    get_shopping_trends,
    compare_keyword_trends,
    get_trending_now
)
from core.storage import list_results, load_result, get_latest_result, save_result


# ============================================================================
# HIGH-LEVEL CONVENIENCE FUNCTIONS
# ============================================================================

def keyword_research(
    keyword: str,
    location_name: str = None,
    include_suggestions: bool = True,
    include_related: bool = True,
    include_difficulty: bool = True
) -> Dict[str, Any]:
    """
    Comprehensive keyword research for a single keyword.

    Performs multiple API calls to gather:
    - Keyword overview (search volume, CPC, competition, search intent)
    - Keyword suggestions (optional)
    - Related keywords (optional)
    - Keyword difficulty (optional)

    Args:
        keyword: The seed keyword to research
        location_name: Target location (default: United States)
        include_suggestions: Include keyword suggestions
        include_related: Include related keywords
        include_difficulty: Include difficulty score

    Returns:
        Dict with keys: overview, suggestions, related, difficulty

    Example:
        >>> result = keyword_research("python programming")
    """
    print(f"\n🔍 Researching keyword: {keyword}")
    results = {}

    # Always get overview
    print("  → Getting keyword overview...")
    results["overview"] = get_keyword_overview(
        keywords=[keyword],
        location_name=location_name
    )

    if include_suggestions:
        print("  → Getting keyword suggestions...")
        results["suggestions"] = get_keyword_suggestions(
            keyword=keyword,
            location_name=location_name,
            limit=50
        )

    if include_related:
        print("  → Getting related keywords...")
        results["related"] = get_related_keywords(
            keyword=keyword,
            location_name=location_name,
            depth=2,
            limit=50
        )

    if include_difficulty:
        print("  → Getting keyword difficulty...")
        results["difficulty"] = get_bulk_keyword_difficulty(
            keywords=[keyword],
            location_name=location_name
        )

    print(f"✅ Research complete for: {keyword}\n")
    return results


def youtube_keyword_research(
    keyword: str,
    location_name: str = None,
    include_serp: bool = True,
    include_trends: bool = True
) -> Dict[str, Any]:
    """
    YouTube-focused keyword research.

    Gathers data specifically useful for YouTube content:
    - Keyword overview with search intent
    - YouTube SERP results (current rankings)
    - YouTube trend data
    - Keyword suggestions

    Args:
        keyword: The keyword to research for YouTube
        location_name: Target location
        include_serp: Include current YouTube rankings
        include_trends: Include YouTube trend data

    Returns:
        Dict with keys: overview, serp, trends, suggestions

    Example:
        >>> result = youtube_keyword_research("video editing tutorial")
    """
    print(f"\n🎬 YouTube keyword research: {keyword}")
    results = {}

    # Keyword overview
    print("  → Getting keyword overview...")
    results["overview"] = get_keyword_overview(
        keywords=[keyword],
        location_name=location_name,
        include_serp_info=True
    )

    # Keyword suggestions
    print("  → Getting keyword suggestions...")
    results["suggestions"] = get_keyword_suggestions(
        keyword=keyword,
        location_name=location_name,
        limit=50
    )

    if include_serp:
        print("  → Getting YouTube rankings...")
        results["youtube_serp"] = get_youtube_serp(
            keyword=keyword,
            location_name=location_name,
            depth=20
        )

    if include_trends:
        print("  → Getting YouTube trends...")
        results["youtube_trends"] = get_youtube_trends(
            keywords=[keyword],
            location_name=location_name
        )

    print(f"✅ YouTube research complete for: {keyword}\n")
    return results


def landing_page_keyword_research(
    keywords: List[str],
    competitor_domain: str = None,
    location_name: str = None
) -> Dict[str, Any]:
    """
    Keyword research for landing page optimization.

    Gathers data useful for landing page SEO:
    - Keyword overview for target keywords
    - Search intent classification
    - Keyword difficulty
    - Google SERP analysis
    - Competitor keywords (if domain provided)

    Args:
        keywords: Target keywords for the landing page
        competitor_domain: Optional competitor domain to analyze
        location_name: Target location

    Returns:
        Dict with comprehensive landing page keyword data

    Example:
        >>> result = landing_page_keyword_research(
        ...     ["best crm software", "crm for small business"],
        ...     competitor_domain="hubspot.com"
        ... )
    """
    print(f"\n📄 Landing page keyword research: {keywords}")
    results = {}

    # Keyword overview
    print("  → Getting keyword overview...")
    results["overview"] = get_keyword_overview(
        keywords=keywords,
        location_name=location_name,
        include_serp_info=True
    )

    # Search intent
    print("  → Getting search intent...")
    results["search_intent"] = get_search_intent(
        keywords=keywords,
        location_name=location_name
    )

    # Difficulty scores
    print("  → Getting keyword difficulty...")
    results["difficulty"] = get_bulk_keyword_difficulty(
        keywords=keywords,
        location_name=location_name
    )

    # SERP analysis for primary keyword
    print("  → Getting SERP analysis...")
    results["serp"] = get_google_serp(
        keyword=keywords[0],
        location_name=location_name
    )

    # Competitor analysis
    if competitor_domain:
        print(f"  → Analyzing competitor: {competitor_domain}...")
        results["competitor_keywords"] = get_keywords_for_site(
            target_domain=competitor_domain,
            location_name=location_name
        )

    print(f"✅ Landing page research complete\n")
    return results


def full_keyword_analysis(
    keywords: List[str],
    location_name: str = None,
    include_historical: bool = True,
    include_trends: bool = True
) -> Dict[str, Any]:
    """
    Full keyword analysis for content strategy.

    Comprehensive analysis including:
    - Keyword overview
    - Historical search volume trends
    - Keyword difficulty
    - Search intent
    - Keyword ideas (expansion)
    - Google Trends data

    Args:
        keywords: Keywords to analyze
        location_name: Target location
        include_historical: Include historical search volume
        include_trends: Include Google Trends data

    Returns:
        Dict with comprehensive keyword analysis

    Example:
        >>> result = full_keyword_analysis(["ai writing tools", "chatgpt alternatives"])
    """
    print(f"\n📊 Full keyword analysis: {keywords}")
    results = {}

    print("  → Getting keyword overview...")
    results["overview"] = get_keyword_overview(
        keywords=keywords,
        location_name=location_name,
        include_serp_info=True
    )

    print("  → Getting keyword difficulty...")
    results["difficulty"] = get_bulk_keyword_difficulty(
        keywords=keywords,
        location_name=location_name
    )

    print("  → Getting search intent...")
    results["search_intent"] = get_search_intent(
        keywords=keywords,
        location_name=location_name
    )

    print("  → Getting keyword ideas...")
    results["keyword_ideas"] = get_keyword_ideas(
        keywords=keywords,
        location_name=location_name,
        limit=100
    )

    if include_historical:
        print("  → Getting historical search volume...")
        results["historical"] = get_historical_search_volume(
            keywords=keywords,
            location_name=location_name
        )

    if include_trends:
        print("  → Getting Google Trends data...")
        results["trends"] = get_trends_explore(
            keywords=keywords[:5],
            location_name=location_name
        )

    print(f"✅ Full analysis complete\n")
    return results


def competitor_analysis(
    domain: str,
    keywords: List[str] = None,
    location_name: str = None
) -> Dict[str, Any]:
    """
    Analyze a competitor's keyword strategy.

    Args:
        domain: Competitor domain to analyze
        keywords: Optional keywords to find competitors for
        location_name: Target location

    Returns:
        Dict with competitor analysis data

    Example:
        >>> result = competitor_analysis("competitor.com")
    """
    print(f"\n🎯 Competitor analysis: {domain}")
    results = {}

    print("  → Getting domain keywords...")
    results["domain_keywords"] = get_domain_keywords(
        target_domain=domain,
        location_name=location_name,
        limit=100
    )

    print("  → Getting keywords from Google Ads data...")
    results["ads_keywords"] = get_keywords_for_site(
        target_domain=domain,
        location_name=location_name
    )

    if keywords:
        print("  → Finding other competitors...")
        results["other_competitors"] = get_competitors(
            keywords=keywords,
            location_name=location_name
        )

    print(f"✅ Competitor analysis complete\n")
    return results


def trending_topics(
    location_name: str = None
) -> Dict[str, Any]:
    """
    Get currently trending topics and searches.

    Args:
        location_name: Target location

    Returns:
        Dict with trending data

    Example:
        >>> result = trending_topics()
    """
    print("\n📈 Getting trending topics...")
    result = get_trending_now(location_name=location_name)
    print("✅ Trending topics retrieved\n")
    return result


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_recent_results(category: str = None, limit: int = 10) -> List[Path]:
    """
    Get recently saved results.

    Args:
        category: Filter by category (keywords_data, labs, serp, trends)
        limit: Maximum results to return

    Returns:
        List of result file paths
    """
    return list_results(category=category, limit=limit)


def load_latest(category: str, operation: str = None) -> Optional[Dict]:
    """
    Load the most recent result for a category/operation.

    Args:
        category: Result category
        operation: Specific operation (optional)

    Returns:
        The loaded result data or None
    """
    return get_latest_result(category=category, operation=operation)


# ============================================================================
# QUICK ACCESS - Direct API function exports
# ============================================================================

# For direct access to individual API functions, import from respective modules:
# from api.keywords_data import get_search_volume, get_keywords_for_site
# from api.labs import get_keyword_suggestions, get_bulk_keyword_difficulty
# from api.serp import get_google_serp, get_youtube_serp
# from api.trends import get_trends_explore, get_youtube_trends
# from api.backlinks import get_backlinks_summary, get_referring_domains


# ============================================================================
# PLAY IMPORTS - Outcome-oriented workflows
# ============================================================================

try:
    from play1_affiliate_kw import affiliate_keyword_miner
except ImportError as e:
    def affiliate_keyword_miner(*a, **kw): raise ImportError(f"Play 1 not available: {e}")

try:
    from play4_competitor_teardown import competitor_teardown
except ImportError as e:
    def competitor_teardown(*a, **kw): raise ImportError(f"Play 4 not available: {e}")

try:
    from play7_local_scraper import local_business_scraper
except ImportError as e:
    def local_business_scraper(*a, **kw): raise ImportError(f"Play 7 not available: {e}")

try:
    from play9_expired_domains import expired_domain_finder
except ImportError as e:
    def expired_domain_finder(*a, **kw): raise ImportError(f"Play 9 not available: {e}")

try:
    from play10_bvs_scorer import bvs_score_domains
except ImportError as e:
    def bvs_score_domains(*a, **kw): raise ImportError(f"Play 10 not available: {e}")

try:
    from play2_content_calendar import build_content_calendar as _play2_calendar
except ImportError:
    _play2_calendar = None

try:
    from play3_serp_features import serp_feature_sniper as _play3_sniper
except ImportError:
    _play3_sniper = None

try:
    from play5_backlink_gap import backlink_gap_finder as _play5_gap
except ImportError:
    _play5_gap = None

try:
    from play6_market_gap import market_gap_finder as _play6_market
except ImportError:
    _play6_market = None

try:
    from play8_local_pack import local_pack_intel as _play8_pack
except ImportError:
    _play8_pack = None


# ============================================================================
# INLINE PLAYS (2, 3, 5, 6, 8) - Lighter workflows using existing API functions
# ============================================================================

def content_calendar(
    domain_or_niche: str,
    months: int = 3,
    location_name: str = None
) -> Dict[str, Any]:
    """
    Play 2 - Build a content calendar for any site or niche.

    Args:
        domain_or_niche: Site domain (e.g. "fifti-fifti.net") or niche keyword ("home decor")
        months: How many months to plan (default 3)
        location_name: Target location

    Returns:
        Dict with month-by-month calendar and markdown output

    Cost: ~$0.01-0.05
    """
    from api.labs import get_keywords_for_site as _labs_kw_site, get_keyword_ideas
    from api.trends import get_trends_explore
    from datetime import datetime, timedelta
    import calendar

    location = location_name or "United States"
    is_domain = "." in domain_or_niche and " " not in domain_or_niche

    print(f"\n📅 Content Calendar Builder: '{domain_or_niche}' ({months} months)")

    # Get keyword pool
    if is_domain:
        print("   Pulling keywords for domain...")
        raw = _labs_kw_site(target_domain=domain_or_niche, location_name=location)
    else:
        print("   Pulling keyword ideas for niche...")
        raw = get_keyword_ideas(keywords=[domain_or_niche], location_name=location, limit=200)

    # Extract keywords
    keywords = []
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    kd = item.get("keyword_data", item)
                    ki = kd.get("keyword_info", {}) or {}
                    kw_text = kd.get("keyword", item.get("keyword", ""))
                    volume = ki.get("search_volume", item.get("search_volume", 0)) or 0
                    cpc = ki.get("cpc", item.get("cpc", 0)) or 0
                    kd_score = kd.get("keyword_properties", {}).get("keyword_difficulty",
                               item.get("keyword_difficulty", 50)) or 50
                    if kw_text and volume > 0:
                        priority = (volume * max(cpc, 0.1)) / max(kd_score, 1)
                        keywords.append({
                            "keyword": kw_text,
                            "volume": volume,
                            "cpc": round(cpc, 2),
                            "kd": kd_score,
                            "priority": round(priority, 2)
                        })
    except Exception as e:
        print(f"   ⚠️  Keyword extraction error: {e}")

    keywords.sort(key=lambda x: x["priority"], reverse=True)
    top_keywords = keywords[:months * 8]  # ~8 posts per month

    # Assign to months
    now = datetime.now()
    calendar_data = {}
    for i in range(months):
        month_date = now.replace(day=1) + timedelta(days=32 * i)
        month_name = month_date.strftime("%B %Y")
        start_idx = i * 8
        month_kws = top_keywords[start_idx:start_idx + 8]
        calendar_data[month_name] = month_kws

    # Build markdown
    lines = [f"# Content Calendar: {domain_or_niche}", f""]
    for month, kws in calendar_data.items():
        lines.extend([f"## {month}", f"", f"| Post | Keyword | Volume | CPC | KD |",
                      f"|------|---------|--------|-----|----|"])
        for j, kw in enumerate(kws, 1):
            lines.append(f"| Post {j} | {kw['keyword']} | {kw['volume']:,} | ${kw['cpc']} | {kw['kd']} |")
        lines.append("")

    result = {
        "domain_or_niche": domain_or_niche,
        "months": months,
        "total_keywords": len(keywords),
        "calendar": calendar_data,
        "markdown": "\n".join(lines)
    }
    save_result(result, category="plays", operation="content_calendar", keyword=domain_or_niche)
    print(f"✅ Calendar built: {len(top_keywords)} posts across {months} months")
    return result


def serp_feature_sniper(
    topic: str,
    keyword_list: Optional[List[str]] = None,
    location_name: str = None
) -> Dict[str, Any]:
    """
    Play 3 - Find winnable SERP features: PAA, featured snippets, image packs.

    Args:
        topic: Topic to research (generates keyword list)
        keyword_list: Optional - provide specific keywords instead
        location_name: Target location

    Returns:
        Dict with PAA questions, featured snippet opps, and winnability scores

    Cost: ~$0.002/keyword
    """
    from api.labs import get_keyword_suggestions
    from api.serp import get_google_serp
    import re

    location = location_name or "United States"
    print(f"\n🎯 SERP Feature Sniper: '{topic}'")

    # Get keywords to check
    if keyword_list:
        keywords_to_check = keyword_list[:10]
    else:
        print("   Getting keyword suggestions...")
        sugg_raw = get_keyword_suggestions(keyword=topic, location_name=location, limit=20)
        keywords_to_check = [topic]
        try:
            tasks = sugg_raw.get("tasks", []) if isinstance(sugg_raw, dict) else []
            for task in tasks:
                for result in task.get("result", []) or []:
                    for item in result.get("items", []) or []:
                        if isinstance(item, dict):
                            kw = item.get("keyword", "")
                            if kw and kw != topic:
                                keywords_to_check.append(kw)
        except Exception:
            pass
        keywords_to_check = keywords_to_check[:8]

    paa_questions = []
    featured_snippets = []
    image_packs = []

    for kw in keywords_to_check:
        print(f"   Checking SERP for: {kw}...")
        try:
            serp_raw = get_google_serp(kw, location_name=location, depth=10, save=False)
            features = _extract_serp_features(serp_raw, kw)
            paa_questions.extend(features["paa"])
            featured_snippets.extend(features["featured_snippets"])
            image_packs.extend(features["image_packs"])
        except Exception as e:
            print(f"   ⚠️  Failed: {e}")

    # Deduplicate PAA
    seen_paa = set()
    unique_paa = []
    for q in paa_questions:
        if q["question"] not in seen_paa:
            seen_paa.add(q["question"])
            unique_paa.append(q)

    lines = [
        f"# SERP Feature Sniper: {topic}",
        f"",
        f"## People Also Ask ({len(unique_paa)} questions)",
        f"",
    ]
    for q in unique_paa[:20]:
        lines.append(f"- **{q['question']}** (keyword: {q['keyword']})")

    if featured_snippets:
        lines.extend([f"", f"## Featured Snippet Opportunities ({len(featured_snippets)})", f""])
        for s in featured_snippets[:10]:
            lines.append(f"- **{s['keyword']}** - Current holder: {s.get('holder_domain', 'unknown')}")

    result = {
        "topic": topic,
        "paa_questions": unique_paa,
        "featured_snippets": featured_snippets,
        "image_packs": image_packs,
        "report": "\n".join(lines)
    }
    save_result(result, category="plays", operation="serp_sniper", keyword=topic)
    print(f"✅ Found {len(unique_paa)} PAA questions, {len(featured_snippets)} snippet opps")
    return result


def _extract_serp_features(serp_raw: Dict, keyword: str) -> Dict:
    """Extract SERP features from organic SERP response."""
    features = {"paa": [], "featured_snippets": [], "image_packs": []}
    try:
        tasks = serp_raw.get("tasks", []) if isinstance(serp_raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("type", "")

                    if item_type == "people_also_ask":
                        items = item.get("items", []) or []
                        for paa_item in items:
                            if isinstance(paa_item, dict):
                                q = paa_item.get("title", paa_item.get("question", ""))
                                if q:
                                    features["paa"].append({
                                        "question": q,
                                        "keyword": keyword,
                                        "featured_title": paa_item.get("featured_title", ""),
                                        "url": paa_item.get("url", "")
                                    })

                    elif item_type == "featured_snippet":
                        holder_url = item.get("url", "")
                        holder_domain = item.get("domain", "")
                        features["featured_snippets"].append({
                            "keyword": keyword,
                            "holder_url": holder_url,
                            "holder_domain": holder_domain,
                            "snippet_text": item.get("description", "")[:200]
                        })

                    elif item_type == "images":
                        features["image_packs"].append({"keyword": keyword})
    except Exception:
        pass
    return features


def backlink_gap_finder(
    your_domain: str,
    competitor_domain: str
) -> Dict[str, Any]:
    """
    Play 5 - Find link opportunities your competitor has that you don't.

    Args:
        your_domain: Your domain
        competitor_domain: Competitor domain

    Returns:
        Dict with gap domains, their DR, and notes

    Cost: ~$0.04 ($0.02 x 2 summaries)
    """
    from api.backlinks import get_domain_intersection, get_backlinks_summary

    print(f"\n🔗 Backlink Gap Finder: {competitor_domain} vs {your_domain}")

    try:
        gap_raw = get_domain_intersection(your_domain, competitor_domain)
        gap_domains = []
        try:
            tasks = gap_raw.get("tasks", []) if isinstance(gap_raw, dict) else []
            for task in tasks:
                for result in task.get("result", []) or []:
                    for item in result.get("items", []) or []:
                        if isinstance(item, dict):
                            gap_domains.append({
                                "domain": item.get("domain", ""),
                                "rank": item.get("rank", 0),
                                "backlinks_to_competitor": item.get("backlinks", 0)
                            })
        except Exception as e:
            print(f"   ⚠️  Gap extraction error: {e}")

        gap_domains.sort(key=lambda x: x.get("rank", 0), reverse=True)

        lines = [
            f"# Backlink Gap: {competitor_domain} vs {your_domain}",
            f"",
            f"{len(gap_domains)} domains link to {competitor_domain} but NOT {your_domain}",
            f"",
            f"| Domain | DR | Links to Competitor |",
            f"|--------|----|--------------------|",
        ]
        for d in gap_domains[:25]:
            lines.append(f"| {d['domain']} | {d.get('rank', 0)} | {d.get('backlinks_to_competitor', 0)} |")

        result = {
            "your_domain": your_domain,
            "competitor_domain": competitor_domain,
            "gap_domains": gap_domains,
            "total_gap": len(gap_domains),
            "report": "\n".join(lines)
        }
        save_result(result, category="plays", operation="backlink_gap",
                    keyword=f"{your_domain}_vs_{competitor_domain}")
        print(f"✅ Found {len(gap_domains)} backlink gap opportunities")
        return result

    except Exception as e:
        print(f"⚠️  Gap finder failed: {e}")
        return {"error": str(e), "gap_domains": []}


def market_gap_finder(
    niche: str,
    location_name: str = None,
    limit: int = 300
) -> Dict[str, Any]:
    """
    Play 6 - Find the best content/affiliate gaps in a niche.

    Args:
        niche: Niche keyword (e.g. "home organization", "dog accessories")
        location_name: Target location
        limit: Max keyword ideas to fetch

    Returns:
        Dict with top 20 gap opportunities ranked by opportunity score

    Cost: ~$0.01-0.04
    """
    from api.labs import get_keyword_ideas, get_search_intent

    location = location_name or "United States"
    print(f"\n🗺️  Market Gap Finder: '{niche}'")

    print("   Fetching keyword ideas...")
    ideas_raw = get_keyword_ideas(keywords=[niche], location_name=location, limit=limit)

    keywords = []
    try:
        tasks = ideas_raw.get("tasks", []) if isinstance(ideas_raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    ki = item.get("keyword_info", {}) or {}
                    volume = ki.get("search_volume", item.get("search_volume", 0)) or 0
                    cpc = ki.get("cpc", item.get("cpc", 0)) or 0
                    kd = item.get("keyword_properties", {}).get("keyword_difficulty",
                         item.get("keyword_difficulty", 100)) or 100
                    if volume > 0:
                        opp = (volume * max(cpc, 0.1)) / max(kd, 1)
                        keywords.append({
                            "keyword": item.get("keyword", ""),
                            "volume": volume,
                            "cpc": round(cpc, 2),
                            "kd": kd,
                            "opportunity_score": round(opp, 2),
                            "competition": ki.get("competition_level", "")
                        })
    except Exception as e:
        print(f"   ⚠️  Extraction error: {e}")

    # Find gaps: high opp score, reasonable KD
    gaps = [k for k in keywords if k["kd"] <= 40 and k["volume"] >= 100]
    gaps.sort(key=lambda x: x["opportunity_score"], reverse=True)
    top_20 = gaps[:20]

    lines = [
        f"# Market Gap Finder: {niche}",
        f"",
        f"**Total keywords analyzed:** {len(keywords)}",
        f"**Gap opportunities (KD <= 40, Vol >= 100):** {len(gaps)}",
        f"",
        f"## Top 20 Gap Opportunities",
        f"",
        f"| # | Keyword | Volume | CPC | KD | Opp Score |",
        f"|---|---------|--------|-----|----|-----------|",
    ]
    for i, kw in enumerate(top_20, 1):
        lines.append(
            f"| {i} | {kw['keyword']} | {kw['volume']:,} | ${kw['cpc']} | {kw['kd']} | {kw['opportunity_score']:.0f} |"
        )

    result = {
        "niche": niche,
        "total_keywords": len(keywords),
        "gaps": gaps,
        "top_20": top_20,
        "report": "\n".join(lines)
    }
    save_result(result, category="plays", operation="market_gap", keyword=niche)
    print(f"✅ Found {len(gaps)} gap opportunities, top 20 in report")
    return result


def local_pack_intel(
    keyword: str,
    city: str,
    your_domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    Play 8 - Competitive analysis for local search results.

    Args:
        keyword: Search keyword (e.g. "dispensary", "vegan restaurant")
        city: Target city (e.g. "Minneapolis, MN")
        your_domain: Optional - check if your domain appears

    Returns:
        Dict with local pack breakdown, winner analysis, and gaps

    Cost: ~$0.004 (maps + organic SERP)
    """
    from api.serp import get_google_maps_serp, get_google_serp

    maps_keyword = f"{keyword} {city}"
    print(f"\n🗺️  Local Pack Intel: '{keyword}' in {city}")

    print("   Pulling Maps SERP...")
    # Maps API: embed city in keyword, no location_name param
    maps_raw = get_google_maps_serp(keyword=maps_keyword, depth=20)

    print("   Pulling Organic SERP...")
    organic_raw = get_google_serp(keyword=maps_keyword, depth=10)

    # Extract local pack
    local_results = []
    try:
        tasks = maps_raw.get("tasks", []) if isinstance(maps_raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict) or item.get("type") == "maps_search_ad":
                        continue
                    rating = item.get("rating", {}) or {}
                    local_results.append({
                        "rank": item.get("rank_group", 0),
                        "name": item.get("title", ""),
                        "website": item.get("url", ""),
                        "phone": item.get("phone", ""),
                        "rating": rating.get("value", "") if isinstance(rating, dict) else str(rating),
                        "reviews": rating.get("votes_count", "") if isinstance(rating, dict) else "",
                        "is_claimed": item.get("is_claimed", False),
                        "address": (item.get("address_info", {}) or {}).get("address", ""),
                    })
    except Exception as e:
        print(f"   ⚠️  Maps extraction error: {e}")

    # Find gaps
    no_website = [b for b in local_results if not b.get("website")]
    low_reviews = [b for b in local_results if isinstance(b.get("reviews"), int) and b["reviews"] < 20]
    unclaimed = [b for b in local_results if not b.get("is_claimed")]

    lines = [
        f"# Local Pack Intel: {keyword} in {city}",
        f"",
        f"## Top Local Results",
        f"",
        f"| Rank | Business | Rating | Reviews | Website |",
        f"|------|----------|--------|---------|---------|",
    ]
    for r in local_results[:10]:
        lines.append(
            f"| {r['rank']} | {r['name']} | {r.get('rating', '-')} | "
            f"{r.get('reviews', '-')} | {'✅' if r.get('website') else '❌ None'} |"
        )

    lines.extend([
        f"",
        f"## Competitive Gaps",
        f"",
        f"**No website:** {len(no_website)} businesses (beatable!)",
        f"**Under 20 reviews:** {len(low_reviews)} businesses",
        f"**Unclaimed listings:** {len(unclaimed)} listings",
    ])

    result = {
        "keyword": keyword,
        "city": city,
        "local_results": local_results,
        "gaps": {"no_website": no_website, "low_reviews": low_reviews, "unclaimed": unclaimed},
        "report": "\n".join(lines)
    }
    save_result(result, category="plays", operation="local_pack", keyword=f"{keyword}_{city}")
    print(f"✅ {len(local_results)} local results. {len(no_website)} have no website (opportunity!)")
    return result


# ============================================================================
# ALWAYS-ON UTILITIES
# ============================================================================

def rank_check(
    domain: str,
    keywords: List[str],
    location_name: str = None
) -> Dict[str, Any]:
    """
    Check current rankings for a domain + keyword list.

    Args:
        domain: Your domain to check
        keywords: Keywords to check rankings for
        location_name: Target location

    Returns:
        Dict with ranking positions per keyword

    Cost: ~$0.002/keyword
    """
    location = location_name or "United States"
    print(f"\n📍 Rank Check: {domain} for {len(keywords)} keywords")

    rankings = []
    for kw in keywords:
        try:
            serp_raw = get_google_serp(kw, location_name=location, depth=100, save=False)
            position = _find_domain_position(serp_raw, domain)
            rankings.append({
                "keyword": kw,
                "position": position,
                "ranking": "Not found in top 100" if position == -1 else f"#{position}"
            })
            print(f"   '{kw}' -> {rankings[-1]['ranking']}")
        except Exception as e:
            rankings.append({"keyword": kw, "position": -1, "error": str(e)})

    result = {"domain": domain, "keywords": keywords, "rankings": rankings}
    save_result(result, category="plays", operation="rank_check", keyword=domain)
    return result


def _find_domain_position(serp_raw: Dict, domain: str) -> int:
    """Find domain position in SERP results. Returns -1 if not found."""
    try:
        tasks = serp_raw.get("tasks", []) if isinstance(serp_raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    item_domain = item.get("domain", "") or ""
                    item_url = item.get("url", "") or ""
                    if domain in item_domain or domain in item_url:
                        return item.get("rank_group", item.get("position", -1))
    except Exception:
        pass
    return -1


def youtube_gap_finder(
    topic: str,
    location_name: str = None
) -> Dict[str, Any]:
    """
    Find missing video content in a niche - YouTube keywords with low competition.

    Args:
        topic: Topic to research for YouTube
        location_name: Target location

    Returns:
        Dict with YouTube keyword gaps and opportunities
    """
    from api.serp import get_youtube_serp
    from api.labs import get_keyword_suggestions

    location = location_name or "United States"
    print(f"\n🎬 YouTube Gap Finder: '{topic}'")

    print("   Getting keyword suggestions...")
    sugg_raw = get_keyword_suggestions(keyword=topic, location_name=location, limit=30)

    keywords = [topic]
    try:
        tasks = sugg_raw.get("tasks", []) if isinstance(sugg_raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if isinstance(item, dict):
                        kw = item.get("keyword", "")
                        if kw:
                            keywords.append(kw)
    except Exception:
        pass

    keywords = keywords[:10]
    gaps = []
    for kw in keywords:
        try:
            yt_raw = get_youtube_serp(kw, location_name=location, depth=10, save=False)
            video_count = 0
            try:
                tasks = yt_raw.get("tasks", []) if isinstance(yt_raw, dict) else []
                for task in tasks:
                    for result in task.get("result", []) or []:
                        video_count = len(result.get("items", []))
            except Exception:
                pass
            gaps.append({
                "keyword": kw,
                "video_count_top10": video_count,
                "gap_score": max(0, 10 - video_count) * 10
            })
            print(f"   '{kw}' -> {video_count} videos in top 10")
        except Exception as e:
            print(f"   ⚠️  '{kw}' failed: {e}")

    gaps.sort(key=lambda x: x["gap_score"], reverse=True)
    result = {"topic": topic, "youtube_gaps": gaps}
    save_result(result, category="plays", operation="youtube_gap", keyword=topic)
    return result


def trend_watch(
    topics: List[str],
    location_name: str = None
) -> Dict[str, Any]:
    """
    Get trending data for content ideas.

    Args:
        topics: List of topics to track (max 5 per Trends task)
        location_name: Target location

    Returns:
        Dict with trend data per topic

    Cost: ~$0.001/5 keywords
    """
    from api.trends import get_trends_explore

    location = location_name or "United States"
    print(f"\n📈 Trend Watch: {topics}")

    results = {}
    # Process in batches of 5 (Trends API limit)
    for i in range(0, len(topics), 5):
        batch = topics[i:i+5]
        try:
            trends_raw = get_trends_explore(keywords=batch, location_name=location)
            try:
                tasks = trends_raw.get("tasks", []) if isinstance(trends_raw, dict) else []
                for task in tasks:
                    for result in task.get("result", []) or []:
                        kw = result.get("keyword", "")
                        data = result.get("data", []) or []
                        if kw and data:
                            peak = max(data, key=lambda x: (x.get("values", [0]) or [0])[0])
                            results[kw] = {
                                "peak_month": peak.get("date_to", "")[:7],
                                "current_value": (data[-1].get("values", [0]) or [0])[0] if data else 0,
                                "peak_value": (peak.get("values", [0]) or [0])[0],
                            }
            except Exception:
                pass
        except Exception as e:
            print(f"   ⚠️  Trends batch failed: {e}")

    result = {"topics": topics, "trends": results}
    save_result(result, category="plays", operation="trend_watch", keyword=topics[0] if topics else "batch")
    return result


def onpage_audit(url: str) -> Dict[str, Any]:
    """
    Basic technical SEO audit via OnPage API.

    Args:
        url: URL to audit (full URL with https://)

    Returns:
        Dict with on-page SEO signals

    Cost: ~$0.000125/page
    """
    from dataforseo_client.api.on_page_api import OnPageApi
    from core.client import get_client

    client = get_client()
    api = OnPageApi(client.api_client)

    print(f"\n🔍 OnPage Audit: {url}")
    try:
        # Start crawl task for single page
        response = api.task_post([{
            "target": url,
            "max_crawl_pages": 1,
            "load_resources": True,
            "enable_javascript": True
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response
        task_id = None
        try:
            task_id = result["tasks"][0]["id"]
        except Exception:
            pass

        audit_result = {"url": url, "task_id": task_id, "raw": result}
        save_result(audit_result, category="plays", operation="onpage_audit", keyword=url)
        print(f"✅ OnPage audit task created: {task_id}")
        return audit_result

    except Exception as e:
        print(f"⚠️  OnPage audit failed: {e}")
        return {"url": url, "error": str(e)}


if __name__ == "__main__":
    print("""
DataForSEO API Toolkit - 10 Plays Edition
==========================================

PLAYS (outcome-oriented):
  play1: affiliate_keyword_miner("home organization", cpc_floor=1.0, kd_ceiling=40)
  play2: content_calendar("fifti-fifti.net", months=3)
  play3: serp_feature_sniper("home organization tips")
  play4: competitor_teardown("overstock.com", your_domain="fifti-fifti.net")
  play5: backlink_gap_finder("fifti-fifti.net", "thespruce.com")
  play6: market_gap_finder("home decor")
  play7: local_business_scraper("church", state="Minnesota")
  play8: local_pack_intel("dispensary", "Minneapolis, MN")
  play9: expired_domain_finder("home organization blog")
  play10: bvs_score_domains("leads.csv")

UTILITIES:
  rank_check("fifti-fifti.net", ["home organization ideas"])
  youtube_gap_finder("home organization tips")
  trend_watch(["home organization", "storage solutions"])
  onpage_audit("https://fifti-fifti.net/home-organization/")

CLASSIC:
  keyword_research("home organization")
  competitor_analysis("thespruce.com")
  trending_topics()

Usage:
  from main import *
  result = affiliate_keyword_miner("home organization")
  print(result["summary"])
""")
