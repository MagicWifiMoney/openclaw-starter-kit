"""
Play 7 - Local Business Scraper

Scrape any category of local businesses across any city list.
Generalized version of the church/dispensary scraping pipeline.

Usage:
    from play7_local_scraper import local_business_scraper
    result = local_business_scraper("church", cities=["Minneapolis, MN", "St. Paul, MN"])
    result = local_business_scraper("vegan restaurant", state="Minnesota")
    result = local_business_scraper("dispensary", cities=["Denver, CO", "Boulder, CO"])
"""
import sys
import csv
import json
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

sys.path.insert(0, str(Path(__file__).parent))

from api.serp import get_google_maps_serp
from core.storage import save_result
from config.settings import settings

# Major US cities by state for state-level scraping
US_CITIES_BY_STATE = {
    "Minnesota": ["Minneapolis, MN", "St. Paul, MN", "Rochester, MN", "Duluth, MN",
                  "Bloomington, MN", "Plymouth, MN", "Brooklyn Park, MN", "Maple Grove, MN",
                  "Eagan, MN", "Coon Rapids, MN", "Burnsville, MN", "Eden Prairie, MN",
                  "Blaine, MN", "Woodbury, MN", "St. Cloud, MN", "Moorhead, MN",
                  "Mankato, MN", "Apple Valley, MN", "Maplewood, MN", "Lakeville, MN"],
    "Colorado": ["Denver, CO", "Colorado Springs, CO", "Aurora, CO", "Fort Collins, CO",
                 "Lakewood, CO", "Thornton, CO", "Arvada, CO", "Westminster, CO",
                 "Boulder, CO", "Centennial, CO", "Pueblo, CO", "Highlands Ranch, CO"],
    "California": ["Los Angeles, CA", "San Diego, CA", "San Jose, CA", "San Francisco, CA",
                   "Fresno, CA", "Sacramento, CA", "Long Beach, CA", "Oakland, CA",
                   "Bakersfield, CA", "Anaheim, CA", "Santa Ana, CA", "Riverside, CA"],
    "Texas": ["Houston, TX", "San Antonio, TX", "Dallas, TX", "Austin, TX",
              "Fort Worth, TX", "El Paso, TX", "Arlington, TX", "Corpus Christi, TX",
              "Plano, TX", "Lubbock, TX", "Irving, TX", "Laredo, TX"],
    "Florida": ["Jacksonville, FL", "Miami, FL", "Tampa, FL", "Orlando, FL",
                "St. Petersburg, FL", "Hialeah, FL", "Tallahassee, FL", "Fort Lauderdale, FL",
                "Port St. Lucie, FL", "Cape Coral, FL", "Pembroke Pines, FL", "Miramar, FL"],
    "Illinois": ["Chicago, IL", "Aurora, IL", "Joliet, IL", "Naperville, IL",
                 "Rockford, IL", "Elgin, IL", "Springfield, IL", "Peoria, IL"],
    "Ohio": ["Columbus, OH", "Cleveland, OH", "Cincinnati, OH", "Toledo, OH",
             "Akron, OH", "Dayton, OH", "Parma, OH", "Canton, OH"],
    "Michigan": ["Detroit, MI", "Grand Rapids, MI", "Warren, MI", "Sterling Heights, MI",
                 "Ann Arbor, MI", "Lansing, MI", "Flint, MI", "Dearborn, MI"],
}


def local_business_scraper(
    business_type: str,
    cities: Optional[List[str]] = None,
    state: Optional[str] = None,
    depth: int = 100,
    language_name: str = "English",
    concurrent: int = 3,
    deduplicate: bool = True
) -> Dict[str, Any]:
    """
    Scrape any category of local businesses across a city list.

    Args:
        business_type: What to search for (e.g. "church", "dispensary", "vegan restaurant")
        cities: List of cities to scrape (e.g. ["Minneapolis, MN", "Denver, CO"])
        state: US state name to use preset city list (e.g. "Minnesota")
        depth: Results per city, max 100 (default 100)
        language_name: Language (default "English")
        concurrent: Concurrent API requests (default 3)
        deduplicate: Remove duplicate businesses by place_id + website (default True)

    Returns:
        Dict with:
            - businesses: list of all unique businesses found
            - total: total count
            - cities_scraped: list of cities processed
            - csv_path: path to saved CSV

    Cost estimate: $0.002/city (100 results each)

    Example:
        >>> result = local_business_scraper("church", state="Minnesota")
        >>> result = local_business_scraper("dispensary", cities=["Denver, CO", "Boulder, CO"])
        >>> result = local_business_scraper("vegan restaurant", cities=["Minneapolis, MN", "Chicago, IL"])
    """
    # Resolve city list
    if cities:
        city_list = cities
    elif state:
        city_list = US_CITIES_BY_STATE.get(state, [])
        if not city_list:
            print(f"⚠️  State '{state}' not in preset list. Add it to US_CITIES_BY_STATE or pass cities= directly.")
            return {"businesses": [], "total": 0, "cities_scraped": [], "csv_path": None}
    else:
        raise ValueError("Provide either 'cities' list or 'state' name")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results" / "plays"
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🗺️  Local Business Scraper: '{business_type}'")
    print(f"   Cities: {len(city_list)} | Depth: {depth}/city")
    print(f"   Est. cost: ${len(city_list) * 0.002:.3f}")

    all_businesses = []
    seen_ids: Set[str] = set()
    cities_scraped = []

    # Process cities in batches
    for i, city in enumerate(city_list):
        # Embed city in keyword (Maps API doesn't accept location_name)
        keyword = f"{business_type} {city}"
        print(f"\n   [{i+1}/{len(city_list)}] {city}...")
        try:
            raw = get_google_maps_serp(
                keyword=keyword,
                depth=min(depth, 100),
                save=False
            )
            businesses = _extract_businesses(raw, city)
            new_count = 0
            for biz in businesses:
                dedup_key = biz.get("place_id") or biz.get("website") or biz.get("name", "")
                if deduplicate and dedup_key and dedup_key in seen_ids:
                    continue
                if dedup_key:
                    seen_ids.add(dedup_key)
                all_businesses.append(biz)
                new_count += 1
            print(f"      {new_count} new businesses (total: {len(all_businesses)})")
            cities_scraped.append(city)
        except Exception as e:
            print(f"      ⚠️  Failed: {e}")

    # Save CSV
    csv_path = results_dir / f"{timestamp}__local_scraper__{business_type.replace(' ', '_')}.csv"
    _save_businesses_csv(all_businesses, csv_path)

    # Save JSON
    full_result = {
        "business_type": business_type,
        "cities_scraped": cities_scraped,
        "total": len(all_businesses),
        "businesses": all_businesses,
        "csv_path": str(csv_path)
    }
    save_result(full_result, category="plays", operation="local_scraper", keyword=business_type)

    print(f"\n✅ Done! {len(all_businesses)} unique {business_type}s across {len(cities_scraped)} cities")
    print(f"   CSV: {csv_path.name}")

    return full_result


def _extract_businesses(raw: Dict, city: str) -> List[Dict]:
    """Extract business listings from Maps SERP response."""
    businesses = []
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    # Skip ads
                    if item.get("type") == "maps_search_ad":
                        continue

                    address_info = item.get("address_info", {}) or {}
                    rating_distribution = item.get("rating_distribution", {}) or {}

                    biz = {
                        "name": item.get("title", ""),
                        "place_id": item.get("place_id", ""),
                        "website": item.get("url", "") or item.get("domain", ""),
                        "phone": item.get("phone", ""),
                        "address": address_info.get("address", ""),
                        "city": address_info.get("city", city.split(",")[0]),
                        "state": address_info.get("region", ""),
                        "zip": address_info.get("zip", ""),
                        "rating": item.get("rating", {}).get("value", "") if isinstance(item.get("rating"), dict) else item.get("rating", ""),
                        "reviews": item.get("rating", {}).get("votes_count", "") if isinstance(item.get("rating"), dict) else "",
                        "latitude": item.get("latitude", ""),
                        "longitude": item.get("longitude", ""),
                        "category": item.get("category", ""),
                        "rank": item.get("rank_group", ""),
                        "scraped_city": city,
                        "is_claimed": item.get("is_claimed", ""),
                    }
                    businesses.append(biz)
    except Exception as e:
        print(f"         ⚠️  Extraction error: {e}")
    return businesses


def _save_businesses_csv(businesses: List[Dict], path: Path):
    """Save businesses to CSV."""
    if not businesses:
        print("   No businesses to save.")
        return

    fieldnames = ["name", "website", "phone", "address", "city", "state", "zip",
                  "rating", "reviews", "category", "place_id", "latitude", "longitude",
                  "rank", "scraped_city", "is_claimed"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(businesses)


if __name__ == "__main__":
    import sys
    btype = sys.argv[1] if len(sys.argv) > 1 else "church"
    state = sys.argv[2] if len(sys.argv) > 2 else "Minnesota"
    result = local_business_scraper(btype, state=state)
    print(f"\nTotal: {result['total']} businesses")
    if result["businesses"]:
        print(f"First 3:")
        for b in result["businesses"][:3]:
            print(f"  - {b['name']} | {b['website']} | {b['phone']}")
