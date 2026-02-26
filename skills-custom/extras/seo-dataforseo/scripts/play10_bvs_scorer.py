"""
Play 10 - Bulk Domain BVS Scorer

Score any list of domains for outreach/acquisition value.
Generalized from the church outreach pipeline — works for any niche.

Usage:
    from play10_bvs_scorer import bvs_score_domains
    result = bvs_score_domains("churches.csv")
    result = bvs_score_domains("leads.csv", target_site="fifti-fifti.net")

Input CSV must have a column named: domain, website, or url
"""
import sys
import csv
import asyncio
import aiohttp
import ssl
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from api.backlinks import get_backlinks_summary
from core.storage import save_result
from config.settings import settings

# BVS Scoring weights
PILLAR_WEIGHTS = {
    "web_presence": 0.25,    # Has website, SSL, mobile-friendly
    "content_signals": 0.25,  # Blog, staff page, newsletter, resources
    "social_signals": 0.20,   # Has social accounts
    "authority": 0.30,        # Backlink rank / referring domains
}

# Tiers based on BVS score (0-100)
TIER_MAP = [
    (75, "gold"),
    (50, "silver"),
    (30, "bronze"),
    (0, "skip"),
]


async def _check_domain_http(session: aiohttp.ClientSession, domain: str) -> Dict:
    """Check a domain for web presence signals via HTTP."""
    signals = {
        "domain": domain,
        "has_website": False,
        "has_ssl": False,
        "has_blog": False,
        "has_contact_form": False,
        "has_staff_page": False,
        "has_newsletter": False,
        "has_facebook": False,
        "has_instagram": False,
        "has_twitter": False,
        "has_youtube": False,
        "mobile_friendly": False,
        "http_status": 0,
        "error": None
    }

    # Normalize domain
    domain = domain.strip().lstrip("https://").lstrip("http://").lstrip("www.").rstrip("/")
    if not domain:
        return signals

    # Try HTTPS first, then HTTP
    for protocol in ["https", "http"]:
        url = f"{protocol}://{domain}"
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.get(url, timeout=timeout, allow_redirects=True,
                                   ssl=False, max_redirects=5) as resp:
                signals["http_status"] = resp.status
                signals["has_website"] = resp.status < 400
                signals["has_ssl"] = str(resp.url).startswith("https")

                if resp.status < 400:
                    try:
                        html = await resp.text(encoding="utf-8", errors="replace")
                        html_lower = html.lower()

                        # Content signals
                        signals["has_blog"] = any(x in html_lower for x in [
                            "/blog", "/news", "/articles", "/posts", "blog."])
                        signals["has_contact_form"] = any(x in html_lower for x in [
                            "contact", "contact-us", "get in touch", "reach us"])
                        signals["has_staff_page"] = any(x in html_lower for x in [
                            "staff", "team", "pastor", "leadership", "about-us", "meet"])
                        signals["has_newsletter"] = any(x in html_lower for x in [
                            "newsletter", "subscribe", "mailing list", "email list"])

                        # Social signals
                        signals["has_facebook"] = "facebook.com" in html_lower
                        signals["has_instagram"] = "instagram.com" in html_lower
                        signals["has_twitter"] = "twitter.com" in html_lower or "x.com" in html_lower
                        signals["has_youtube"] = "youtube.com" in html_lower

                        # Mobile friendly (basic check for viewport meta)
                        signals["mobile_friendly"] = "viewport" in html_lower

                    except Exception:
                        pass
                    break  # Got a good response, don't try http

        except asyncio.TimeoutError:
            signals["error"] = "timeout"
        except Exception as e:
            signals["error"] = str(e)[:100]

    return signals


async def _check_all_domains(domains: List[str], concurrent: int = 5) -> List[Dict]:
    """Async check all domains concurrently."""
    connector = aiohttp.TCPConnector(limit=concurrent, ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BottiSEO/1.0; outreach-research)"
    }

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        semaphore = asyncio.Semaphore(concurrent)

        async def check_with_sem(domain):
            async with semaphore:
                return await _check_domain_http(session, domain)

        tasks = [check_with_sem(d) for d in domains]
        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)
            if (i + 1) % 10 == 0:
                print(f"      HTTP checked: {i+1}/{len(domains)}")
        return results


def _score_domain(http_signals: Dict, bl_metrics: Dict) -> Dict:
    """Calculate BVS score from HTTP + backlink signals."""
    domain = http_signals.get("domain", "")

    # Pillar 1: Web Presence (0-100)
    web_presence = 0
    if http_signals.get("has_website"):
        web_presence += 40
    if http_signals.get("has_ssl"):
        web_presence += 20
    if http_signals.get("mobile_friendly"):
        web_presence += 20
    if http_signals.get("http_status", 0) == 200:
        web_presence += 20

    # Pillar 2: Content Signals (0-100)
    content_signals = 0
    if http_signals.get("has_blog"):
        content_signals += 30
    if http_signals.get("has_contact_form"):
        content_signals += 25
    if http_signals.get("has_staff_page"):
        content_signals += 25
    if http_signals.get("has_newsletter"):
        content_signals += 20

    # Pillar 3: Social Signals (0-100)
    social_signals = 0
    social_count = sum([
        http_signals.get("has_facebook", False),
        http_signals.get("has_instagram", False),
        http_signals.get("has_twitter", False),
        http_signals.get("has_youtube", False),
    ])
    social_signals = min(social_count * 25, 100)

    # Pillar 4: Authority (0-100, based on DR)
    rank = bl_metrics.get("rank", 0) or 0
    rd = bl_metrics.get("referring_domains", 0) or 0
    spam = bl_metrics.get("spam_score", 100) or 100

    authority = 0
    if rank > 0:
        # Scale: DR 50+ = 80pts, DR 30+ = 60pts, DR 10+ = 30pts
        if rank >= 50:
            authority = 80
        elif rank >= 30:
            authority = 60
        elif rank >= 20:
            authority = 45
        elif rank >= 10:
            authority = 30
        else:
            authority = 15
        # Bonus for many referring domains
        if rd >= 100:
            authority = min(authority + 15, 100)
        elif rd >= 50:
            authority = min(authority + 10, 100)
        # Penalty for high spam
        if spam > 50:
            authority = max(authority - 30, 0)
        elif spam > 30:
            authority = max(authority - 15, 0)

    # Weighted BVS
    bvs = (
        web_presence * PILLAR_WEIGHTS["web_presence"] +
        content_signals * PILLAR_WEIGHTS["content_signals"] +
        social_signals * PILLAR_WEIGHTS["social_signals"] +
        authority * PILLAR_WEIGHTS["authority"]
    )
    bvs = round(bvs, 1)

    # Assign tier
    tier = "skip"
    for threshold, tier_name in TIER_MAP:
        if bvs >= threshold:
            tier = tier_name
            break

    return {
        "domain": domain,
        "bvs": bvs,
        "tier": tier,
        "pillar_web": round(web_presence, 0),
        "pillar_content": round(content_signals, 0),
        "pillar_social": round(social_signals, 0),
        "pillar_authority": round(authority, 0),
        "dr": rank,
        "rd": rd,
        "spam_score": spam,
        "has_ssl": http_signals.get("has_ssl", False),
        "has_blog": http_signals.get("has_blog", False),
        "has_contact": http_signals.get("has_contact_form", False),
        "has_staff": http_signals.get("has_staff_page", False),
        "has_newsletter": http_signals.get("has_newsletter", False),
        "facebook": http_signals.get("has_facebook", False),
        "instagram": http_signals.get("has_instagram", False),
        "website": http_signals.get("has_website", False),
        "http_status": http_signals.get("http_status", 0),
        "error": http_signals.get("error", ""),
    }


def bvs_score_domains(
    csv_input_path: str,
    target_site: Optional[str] = None,
    concurrent: int = 5,
    skip_http: bool = False,
    skip_backlinks: bool = False
) -> Dict[str, Any]:
    """
    Score a list of domains for outreach/acquisition value.

    Args:
        csv_input_path: Path to input CSV with domain/website/url column
        target_site: Optional - your site (for context in report, future relevance scoring)
        concurrent: Concurrent HTTP checks (default 5)
        skip_http: Skip HTTP scraping (faster, less signal)
        skip_backlinks: Skip backlink check (faster, cheaper)

    Returns:
        Dict with:
            - scored: list of all domains with BVS scores + tier
            - by_tier: dict of gold/silver/bronze/skip lists
            - csv_path: path to enriched output CSV
            - summary: markdown summary

    Cost estimate: $0.02/domain for backlinks (HTTP is free)

    Example:
        >>> result = bvs_score_domains("leads/churches.csv")
        >>> result = bvs_score_domains("outreach/competitors.csv", target_site="fifti-fifti.net")
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results" / "plays"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load input CSV
    input_path = Path(csv_input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_input_path}")

    domains = _load_domains_from_csv(input_path)
    print(f"\n📊 BVS Domain Scorer")
    print(f"   Input: {len(domains)} domains from {input_path.name}")
    if target_site:
        print(f"   Target site: {target_site}")
    print(f"   Est. cost: ${len(domains) * 0.02:.2f} (backlinks)")

    # HTTP checks
    http_results: Dict[str, Dict] = {}
    if not skip_http:
        print(f"\n[1/3] HTTP scanning {len(domains)} domains (concurrent={concurrent})...")
        raw_http = asyncio.run(_check_all_domains(domains, concurrent=concurrent))
        for item in raw_http:
            http_results[item["domain"]] = item
        print(f"      Done. {sum(1 for v in http_results.values() if v.get('has_website'))} have active websites")
    else:
        print("\n[1/3] Skipping HTTP scan (skip_http=True)")
        for d in domains:
            http_results[d] = {"domain": d}

    # Backlink checks
    bl_results: Dict[str, Dict] = {}
    if not skip_backlinks:
        print(f"\n[2/3] Backlink checks for {len(domains)} domains...")
        for i, domain in enumerate(domains):
            print(f"   [{i+1}/{len(domains)}] {domain}...")
            try:
                bl_raw = get_backlinks_summary(domain, save=False)
                bl_results[domain] = _extract_bl_metrics(bl_raw)
            except Exception as e:
                print(f"      ⚠️  Failed: {e}")
                bl_results[domain] = {}
    else:
        print("\n[2/3] Skipping backlink check (skip_backlinks=True)")
        for d in domains:
            bl_results[d] = {}

    # Score all domains
    print("\n[3/3] Scoring all domains...")
    scored = []
    for domain in domains:
        http = http_results.get(domain, {"domain": domain})
        bl = bl_results.get(domain, {})
        score = _score_domain(http, bl)
        scored.append(score)

    # Sort by BVS
    scored.sort(key=lambda x: x.get("bvs", 0), reverse=True)

    # Group by tier
    by_tier = {"gold": [], "silver": [], "bronze": [], "skip": []}
    for s in scored:
        tier = s.get("tier", "skip")
        by_tier[tier].append(s)

    print(f"\n   Tier breakdown:")
    for tier, items in by_tier.items():
        print(f"   {tier.upper()}: {len(items)}")

    # Save output CSV
    output_name = f"{timestamp}__bvs__{input_path.stem}.csv"
    csv_path = results_dir / output_name
    _save_scored_csv(scored, csv_path)

    # Build summary
    summary = _build_bvs_summary(scored, by_tier, target_site)

    full_result = {
        "total": len(scored),
        "scored": scored,
        "by_tier": by_tier,
        "csv_path": str(csv_path),
        "summary": summary
    }
    save_result(full_result, category="plays", operation="bvs_scorer", keyword=input_path.stem)

    print(f"\n✅ BVS scoring complete. CSV: {csv_path.name}")
    print(summary[:600])

    return full_result


def _load_domains_from_csv(path: Path) -> List[str]:
    """Load domains from CSV, detecting column name automatically."""
    domains = []
    possible_cols = ["domain", "website", "url", "Domain", "Website", "URL"]
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        domain_col = None
        for col in possible_cols:
            if col in fieldnames:
                domain_col = col
                break
        if not domain_col:
            domain_col = fieldnames[0] if fieldnames else None

        if not domain_col:
            raise ValueError(f"No domain/website/url column found in {path.name}")

        for row in reader:
            val = row.get(domain_col, "").strip()
            if val:
                # Normalize to bare domain
                val = re.sub(r"^https?://", "", val)
                val = re.sub(r"^www\.", "", val)
                val = val.rstrip("/").split("/")[0]
                if val:
                    domains.append(val)

    return list(dict.fromkeys(domains))  # Deduplicate while preserving order


def _extract_bl_metrics(raw: Dict) -> Dict:
    """Extract backlink metrics from summary response."""
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
    return {}


def _save_scored_csv(scored: List[Dict], path: Path):
    """Save scored domains to CSV."""
    if not scored:
        return
    fieldnames = ["domain", "tier", "bvs", "dr", "rd", "spam_score",
                  "pillar_web", "pillar_content", "pillar_social", "pillar_authority",
                  "has_ssl", "has_blog", "has_contact", "has_staff", "has_newsletter",
                  "facebook", "instagram", "website", "http_status", "error"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(scored)


def _build_bvs_summary(scored: List[Dict], by_tier: Dict, target_site: Optional[str]) -> str:
    """Build markdown BVS summary."""
    lines = [
        f"# BVS Domain Scoring Report",
        f"",
        f"{'Target site: ' + target_site if target_site else ''}",
        f"",
        f"## Tier Breakdown",
        f"",
        f"| Tier | Count | Action |",
        f"|------|-------|--------|",
        f"| 🥇 Gold (75+) | {len(by_tier['gold'])} | Priority outreach |",
        f"| 🥈 Silver (50-74) | {len(by_tier['silver'])} | Standard outreach |",
        f"| 🥉 Bronze (30-49) | {len(by_tier['bronze'])} | Low priority |",
        f"| ⛔ Skip (<30) | {len(by_tier['skip'])} | Skip |",
        f"",
        f"## Top 20 by BVS Score",
        f"",
        f"| Domain | BVS | Tier | DR | RD | Blog | Contact | Newsletter |",
        f"|--------|-----|------|----|----|------|---------|-----------|",
    ]
    for s in scored[:20]:
        tier_emoji = {"gold": "🥇", "silver": "🥈", "bronze": "🥉", "skip": "⛔"}.get(s.get("tier", "skip"), "")
        lines.append(
            f"| {s.get('domain', '')} | {s.get('bvs', 0)} | {tier_emoji} | "
            f"{s.get('dr', 0)} | {s.get('rd', 0):,} | "
            f"{'✅' if s.get('has_blog') else '❌'} | "
            f"{'✅' if s.get('has_contact') else '❌'} | "
            f"{'✅' if s.get('has_newsletter') else '❌'} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "leads.csv"
    target = sys.argv[2] if len(sys.argv) > 2 else None
    result = bvs_score_domains(csv_path, target_site=target)
