"""
Play 9 - Expired Domain Finder

Find expired/dropped domains with real backlink value in a niche.
Could become a Search Console Tools feature — domains people actually want to buy.

Usage:
    from play9_expired_domains import expired_domain_finder
    result = expired_domain_finder("home organization blog")
    result = expired_domain_finder("pet care", dr_floor=15, max_spam=25)
"""
import sys
import csv
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

sys.path.insert(0, str(Path(__file__).parent))

from api.serp import get_google_serp
from api.backlinks import get_backlinks_summary, get_bulk_backlinks_summary
from core.storage import save_result
from config.settings import settings

# Common patterns for expired/parked domains
EXPIRED_SIGNALS = [
    "godaddy.com/domain", "sedo.com", "dan.com", "afternic.com",
    "flippa.com", "namecheap.com/domains/registration/results",
    "parking", "domain for sale", "this domain is for sale",
    "buy this domain", "domain expired", "account suspended",
    "parked by godaddy", "namebright.com"
]

HOSTED_SIGNALS = [
    "wordpress.com", "wix.com", "squarespace.com", "weebly.com",
    "blogspot.com", "tumblr.com"
]


def expired_domain_finder(
    niche_keywords: str,
    dr_floor: int = 10,
    max_spam: int = 30,
    location_name: str = None,
    serp_depth: int = 100,
    check_domains: int = 30
) -> Dict[str, Any]:
    """
    Find expired/dropped domains with real backlink value in a niche.

    Flow:
    1. Pull organic SERPs for niche keywords (find ranking domains)
    2. Extract all unique domains from results
    3. Get backlink profile for each (DR, RD, spam score)
    4. Filter by DR floor + spam ceiling
    5. Flag potential expired/dropped domains

    Args:
        niche_keywords: Niche keyword(s) to search (e.g. "home organization blog")
        dr_floor: Minimum domain rank to care about (default 10)
        max_spam: Maximum spam score (default 30)
        location_name: Target location (default: United States)
        serp_depth: How deep to go in SERP (default 100)
        check_domains: Max domains to check backlinks for (default 30)

    Returns:
        Dict with:
            - candidates: list of domain candidates with metrics
            - csv_path: path to saved CSV
            - summary: markdown summary

    Cost estimate: ~$0.002 (SERP) + $0.02/domain for backlinks = ~$0.02-0.62

    Example:
        >>> result = expired_domain_finder("home organization tips", dr_floor=15)
        >>> result = expired_domain_finder("minneapolis church blog", dr_floor=5, max_spam=40)
    """
    location = location_name or settings.DEFAULT_LOCATION_NAME
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n🕵️  Expired Domain Finder: '{niche_keywords}'")
    print(f"   Filters: DR >= {dr_floor}, Spam <= {max_spam}")

    results_dir = Path(__file__).parent / "results" / "plays"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Pull organic SERPs for multiple keyword variations
    print("\n[1/3] Pulling organic SERPs...")
    all_domains: Set[str] = set()
    domain_keyword_map: Dict[str, List[str]] = {}

    # Search for multiple related terms
    search_terms = _expand_keywords(niche_keywords)
    print(f"   Searching {len(search_terms)} keyword variations...")

    for term in search_terms:
        try:
            serp_raw = get_google_serp(term, location_name=location, depth=min(serp_depth, 100), save=False)
            domains = _extract_domains_from_serp(serp_raw)
            for d in domains:
                all_domains.add(d)
                if d not in domain_keyword_map:
                    domain_keyword_map[d] = []
                if term not in domain_keyword_map[d]:
                    domain_keyword_map[d].append(term)
            print(f"   '{term}' -> {len(domains)} domains")
        except Exception as e:
            print(f"   ⚠️  SERP failed for '{term}': {e}")

    # Remove obviously irrelevant domains
    all_domains = _filter_irrelevant_domains(all_domains)
    print(f"\n   Found {len(all_domains)} unique domains total")

    # Step 2: Get backlink profiles
    domains_to_check = list(all_domains)[:check_domains]
    print(f"\n[2/3] Checking backlinks for {len(domains_to_check)} domains...")
    print(f"   Est. cost: ${len(domains_to_check) * 0.02:.2f}")

    domain_metrics: Dict[str, Dict] = {}
    for i, domain in enumerate(domains_to_check):
        print(f"   [{i+1}/{len(domains_to_check)}] {domain}...")
        try:
            bl_raw = get_backlinks_summary(domain, save=False)
            metrics = _extract_backlink_metrics(bl_raw)
            metrics["domain"] = domain
            metrics["ranking_keywords"] = domain_keyword_map.get(domain, [])
            domain_metrics[domain] = metrics
            print(f"      DR: {metrics.get('rank', '?')} | "
                  f"RD: {metrics.get('referring_domains', '?')} | "
                  f"Spam: {metrics.get('spam_score', '?')}")
        except Exception as e:
            print(f"      ⚠️  Failed: {e}")

    # Step 3: Filter and score
    print(f"\n[3/3] Filtering and scoring candidates...")
    candidates = []
    for domain, metrics in domain_metrics.items():
        rank = metrics.get("rank", 0) or 0
        spam = metrics.get("spam_score", 100) or 100
        rd = metrics.get("referring_domains", 0) or 0

        if rank < dr_floor:
            continue
        if spam > max_spam:
            continue
        if rd < 3:
            continue

        # Opportunity score = DR * RD / max(spam, 1)
        opp_score = (rank * rd) / max(spam, 1)
        metrics["opportunity_score"] = round(opp_score, 1)
        metrics["niche_keywords"] = len(metrics.get("ranking_keywords", []))
        candidates.append(metrics)

    candidates.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
    print(f"   {len(candidates)} candidates pass filters")

    # Save CSV
    csv_path = results_dir / f"{timestamp}__expired_domains__{niche_keywords[:30].replace(' ', '_')}.csv"
    _save_domains_csv(candidates, csv_path)

    # Build summary
    summary = _build_summary(niche_keywords, candidates, dr_floor, max_spam)

    full_result = {
        "niche_keywords": niche_keywords,
        "filters": {"dr_floor": dr_floor, "max_spam": max_spam},
        "domains_found": len(all_domains),
        "domains_checked": len(domains_to_check),
        "candidates": candidates,
        "csv_path": str(csv_path),
        "summary": summary
    }
    save_result(full_result, category="plays", operation="expired_domains", keyword=niche_keywords)

    print(f"\n✅ Found {len(candidates)} domain candidates")
    print(summary[:800])

    return full_result


def _expand_keywords(keyword: str) -> List[str]:
    """Generate multiple search variations from a seed keyword."""
    base = keyword.strip()
    variations = [
        base,
        f"{base} blog",
        f"best {base}",
        f"{base} tips",
        f"{base} guide",
    ]
    # Deduplicate
    seen = set()
    result = []
    for v in variations:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result[:4]  # Keep to 4 to control cost


def _extract_domains_from_serp(raw: Dict) -> Set[str]:
    """Extract unique domains from SERP results."""
    domains = set()
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    domain = item.get("domain", "") or ""
                    url = item.get("url", "") or ""
                    if not domain and url:
                        # Extract domain from URL
                        match = re.match(r"https?://(?:www\.)?([^/]+)", url)
                        if match:
                            domain = match.group(1)
                    if domain:
                        # Normalize - remove www
                        domain = domain.lstrip("www.")
                        domains.add(domain)
    except Exception:
        pass
    return domains


def _filter_irrelevant_domains(domains: Set[str]) -> Set[str]:
    """Remove obviously irrelevant/mega-authority domains."""
    skip_patterns = [
        "google.", "youtube.", "facebook.", "instagram.", "twitter.", "linkedin.",
        "wikipedia.", "amazon.", "pinterest.", "reddit.", "yelp.", "tripadvisor.",
        "healthline.", "webmd.", "nytimes.", "cnn.", "bbc.", "forbes.", "huffpost.",
        "buzzfeed.", "medium.", "quora.", "stackoverflow.", "github.", "etsy.",
        "walmart.", "target.", "homedepot.", "lowes.", "bestbuy.",
    ]
    filtered = set()
    for domain in domains:
        skip = False
        for pattern in skip_patterns:
            if pattern in domain:
                skip = True
                break
        if not skip:
            filtered.add(domain)
    return filtered


def _extract_backlink_metrics(raw: Dict) -> Dict:
    """Extract metrics from backlinks summary response."""
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                if isinstance(result, dict):
                    return {
                        "rank": result.get("rank", 0) or 0,
                        "backlinks": result.get("backlinks", 0) or 0,
                        "referring_domains": result.get("referring_domains", 0) or 0,
                        "spam_score": result.get("spam_score", 0) or 0,
                    }
    except Exception:
        pass
    return {"rank": 0, "backlinks": 0, "referring_domains": 0, "spam_score": 0}


def _save_domains_csv(candidates: List[Dict], path: Path):
    """Save domain candidates to CSV."""
    if not candidates:
        return
    fieldnames = ["domain", "rank", "backlinks", "referring_domains", "spam_score",
                  "opportunity_score", "niche_keywords", "ranking_keywords"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in candidates:
            row_copy = dict(row)
            if isinstance(row_copy.get("ranking_keywords"), list):
                row_copy["ranking_keywords"] = "; ".join(row_copy["ranking_keywords"])
            writer.writerow(row_copy)


def _build_summary(niche: str, candidates: List[Dict], dr_floor: int, max_spam: int) -> str:
    """Build markdown summary."""
    lines = [
        f"# Expired Domain Finder: {niche}",
        f"",
        f"**Filters:** DR >= {dr_floor} | Spam Score <= {max_spam}",
        f"**Candidates found:** {len(candidates)}",
        f"",
        f"## Top Candidates by Opportunity Score",
        f"",
        f"| Domain | DR | RD | Spam | Opp Score | Niche Keywords |",
        f"|--------|----|----|------|-----------|----------------|",
    ]
    for c in candidates[:20]:
        lines.append(
            f"| {c.get('domain', '')} | {c.get('rank', 0)} | "
            f"{c.get('referring_domains', 0):,} | {c.get('spam_score', 0)} | "
            f"{c.get('opportunity_score', 0):.0f} | {c.get('niche_keywords', 0)} |"
        )
    lines.extend([
        f"",
        f"## How to Verify",
        f"1. Check domain availability at namecheap.com or GoDaddy",
        f"2. Verify Wayback Machine history for content relevance",
        f"3. Check Ahrefs/Moz for additional backlink verification",
        f"4. Look for manual actions in GSC before buying",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    niche = sys.argv[1] if len(sys.argv) > 1 else "home organization blog"
    dr = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    spam = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    result = expired_domain_finder(niche, dr_floor=dr, max_spam=spam)
