"""
Play 8 - Local Pack Intel

Competitive analysis for local search results.
Who's in the 3-pack? What are their ratings, review counts, websites?
Who has gaps you can exploit (no website, low reviews, missing hours)?

Usage:
    from play8_local_pack import local_pack_intel
    result = local_pack_intel("vegan restaurant", "Minneapolis MN")
    result = local_pack_intel("cannabis dispensary", "Minneapolis MN", your_domain="mncannabishub.com")
    result = local_pack_intel("dog groomer", "Austin TX")
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))

from api.serp import get_google_maps_serp, get_google_serp
from core.storage import save_result
from config.settings import settings


def _extract_maps_results(serp_raw: Dict) -> List[Dict]:
    """Pull structured data from a Google Maps SERP response."""
    results = []
    if not serp_raw:
        return results

    items = serp_raw.get("items", []) or []
    for item in items:
        domain = ""
        url = item.get("url", "") or item.get("website", "")
        if url:
            domain = urlparse(url).netloc.replace("www.", "")

        biz = {
            "name":          item.get("title", "") or item.get("name", ""),
            "position":      item.get("rank_absolute", item.get("rank_group", 99)),
            "rating":        item.get("rating", {}).get("value") if isinstance(item.get("rating"), dict) else item.get("rating"),
            "reviews_count": item.get("rating", {}).get("votes_count") if isinstance(item.get("rating"), dict) else item.get("reviews_count", 0),
            "address":       item.get("address", ""),
            "phone":         item.get("phone", ""),
            "website":       url,
            "domain":        domain,
            "place_id":      item.get("place_id", ""),
            "category":      item.get("category", ""),
            "hours":         item.get("work_hours", {}).get("current_status", "") if item.get("work_hours") else "",
            "has_website":   bool(url),
            "is_3pack":      item.get("rank_absolute", 99) <= 3,
        }

        # Weakness flags — opportunities to exploit
        weaknesses = []
        if not biz["has_website"]:
            weaknesses.append("no website")
        if (biz["reviews_count"] or 0) < 10:
            weaknesses.append("few reviews (<10)")
        if not biz["phone"]:
            weaknesses.append("no phone listed")
        if not biz["hours"]:
            weaknesses.append("no hours listed")
        if biz["rating"] and biz["rating"] < 4.0:
            weaknesses.append(f"low rating ({biz['rating']}★)")

        biz["weaknesses"] = weaknesses

        results.append(biz)

    return results


def _check_organic_local(keyword: str, city: str) -> List[Dict]:
    """Check organic SERP for local results (not 3-pack)."""
    try:
        query = f"{keyword} {city}"
        serp = get_google_serp(query, location_name=city, depth=10)
        if not serp:
            return []

        results = []
        for item in (serp.get("items", []) or []):
            if item.get("type") == "organic":
                domain = urlparse(item.get("url", "")).netloc.replace("www.", "")
                results.append({
                    "position": item.get("rank_absolute", 99),
                    "title":    item.get("title", ""),
                    "domain":   domain,
                    "url":      item.get("url", ""),
                })
        return results[:10]
    except Exception:
        return []


def local_pack_intel(
    keyword: str,
    city: str,
    your_domain: Optional[str] = None,
    include_organic: bool = True,
) -> Dict[str, Any]:
    """
    Full local competitive analysis for a keyword + city.

    Args:
        keyword: Search term (e.g. "vegan restaurant", "cannabis dispensary")
        city: Location (e.g. "Minneapolis MN", "Austin TX")
        your_domain: Your domain to check if you appear (optional)
        include_organic: Also pull organic SERP (slightly more expensive)

    Returns:
        Dict with 3-pack results, full local results, weakness analysis, your position
    """
    settings.validate()

    query = f"{keyword} {city}"
    print(f"Local Pack Intel: '{query}'")

    # Maps SERP
    maps_raw = get_google_maps_serp(query, location_name=city)
    all_results = _extract_maps_results(maps_raw)

    pack3      = [r for r in all_results if r["is_3pack"]]
    extended   = [r for r in all_results if not r["is_3pack"]]

    # Check organic if requested
    organic_results = []
    if include_organic:
        organic_results = _check_organic_local(keyword, city)

    # Find your position if domain provided
    your_position = None
    your_maps_result = None
    if your_domain:
        your_domain_clean = your_domain.replace("www.", "")
        for r in all_results:
            if your_domain_clean in r["domain"]:
                your_position = r["position"]
                your_maps_result = r
                break

    # Market analysis
    total_with_website   = sum(1 for r in all_results if r["has_website"])
    total_without        = sum(1 for r in all_results if not r["has_website"])
    avg_rating           = None
    avg_reviews          = None

    rated = [r for r in all_results if r["rating"]]
    if rated:
        avg_rating = round(sum(r["rating"] for r in rated) / len(rated), 1)
    reviewed = [r for r in all_results if r["reviews_count"]]
    if reviewed:
        avg_reviews = round(sum(r["reviews_count"] for r in reviewed) / len(reviewed))

    # Businesses with weaknesses = outreach/content opportunities
    weak_businesses = [r for r in all_results if r["weaknesses"]]

    # 3-pack analysis
    pack3_avg_reviews = None
    if pack3:
        pack3_reviewed = [r for r in pack3 if r["reviews_count"]]
        if pack3_reviewed:
            pack3_avg_reviews = round(sum(r["reviews_count"] for r in pack3_reviewed) / len(pack3_reviewed))

    result = {
        "status":         "success",
        "keyword":        keyword,
        "city":           city,
        "query":          query,
        "pack3":          pack3,
        "extended":       extended,
        "organic":        organic_results,
        "total_results":  len(all_results),
        "total_with_website":  total_with_website,
        "total_without_website": total_without,
        "avg_rating":     avg_rating,
        "avg_reviews":    avg_reviews,
        "pack3_avg_reviews": pack3_avg_reviews,
        "weak_businesses": weak_businesses,
        "your_domain":    your_domain,
        "your_position":  your_position,
        "your_maps_result": your_maps_result,
        "timestamp":      datetime.now().isoformat(),
    }

    save_result(result, category="serp", operation="local_pack",
                keyword=f"{keyword}_{city}".replace(" ", "_").lower())

    # Print summary
    print(f"\n{'='*60}")
    print(f"LOCAL PACK INTEL — {query}")
    print(f"{'='*60}")
    print(f"3-Pack:")
    for r in pack3:
        print(f"  #{r['position']} {r['name']}")
        print(f"     ⭐ {r['rating'] or 'n/a'} ({r['reviews_count'] or 0} reviews) | {r['domain'] or 'NO WEBSITE'}")
        if r["weaknesses"]:
            print(f"     ⚠️  {', '.join(r['weaknesses'])}")

    if extended:
        print(f"\nExtended Results ({len(extended)} businesses):")
        for r in extended[:5]:
            print(f"  #{r['position']} {r['name']} | ⭐{r['rating'] or 'n/a'} ({r['reviews_count'] or 0})")

    print(f"\nMarket stats:")
    print(f"  Avg rating:        {avg_rating}★")
    print(f"  Avg reviews:       {avg_reviews}")
    print(f"  3-pack avg reviews:{pack3_avg_reviews}")
    print(f"  No website:        {total_without}/{len(all_results)}")
    print(f"  Weak businesses:   {len(weak_businesses)}")

    if your_domain:
        if your_position:
            print(f"\n✅ YOUR POSITION: #{your_position} for '{query}'")
        else:
            print(f"\n❌ {your_domain} not found in local results for '{query}'")

    if weak_businesses:
        print(f"\nOPPORTUNITIES (businesses with gaps):")
        for r in weak_businesses[:5]:
            print(f"  {r['name']}: {', '.join(r['weaknesses'])}")

    return result
