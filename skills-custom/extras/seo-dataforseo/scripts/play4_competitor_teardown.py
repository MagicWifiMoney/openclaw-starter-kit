"""
Play 4 - Competitor Teardown

Full competitive intelligence on any domain.
Optional gap analysis if you provide your own domain.

Usage:
    from play4_competitor_teardown import competitor_teardown
    result = competitor_teardown("fifti-fifti.net")
    result = competitor_teardown("competitor.com", your_domain="mysite.com")
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

sys.path.insert(0, str(Path(__file__).parent))

from api.labs import get_domain_keywords, get_keyword_overview
from api.backlinks import get_backlinks_summary, get_domain_pages
from core.storage import save_result
from config.settings import settings


def competitor_teardown(
    competitor_domain: str,
    your_domain: Optional[str] = None,
    location_name: str = None,
    kw_limit: int = 100,
    pages_limit: int = 20
) -> Dict[str, Any]:
    """
    Full competitive intelligence report on a domain.

    Args:
        competitor_domain: Domain to analyze (e.g. "competitor.com")
        your_domain: Your domain for gap analysis (optional)
        location_name: Target location (default: United States)
        kw_limit: Max keywords to pull (default 100)
        pages_limit: Max top pages to pull (default 20)

    Returns:
        Dict with:
            - competitor_keywords: their top ranking keywords
            - top_pages: their top pages by backlinks
            - backlink_profile: DR, RD, backlinks, spam score
            - gaps: keywords they rank for that you don't (if your_domain given)
            - report: full markdown report

    Cost estimate: ~$0.05-0.15 per teardown

    Example:
        >>> result = competitor_teardown("overstock.com", your_domain="fifti-fifti.net")
    """
    location = location_name or settings.DEFAULT_LOCATION_NAME
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n🔬 Competitor Teardown: {competitor_domain}")
    if your_domain:
        print(f"   Gap analysis vs: {your_domain}")

    results_dir = Path(__file__).parent / "results" / "plays"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Keywords they rank for
    print("\n[1/4] Pulling their organic keyword rankings...")
    comp_keywords_raw = get_domain_keywords(
        target_domain=competitor_domain,
        location_name=location,
        limit=kw_limit,
        save=True
    )
    comp_keywords = _extract_domain_keywords(comp_keywords_raw)
    print(f"      Got {len(comp_keywords)} keywords")

    # Step 2: Your keywords (for gap analysis)
    your_keywords = set()
    if your_domain:
        print(f"\n[2/4] Pulling your keyword rankings ({your_domain})...")
        your_kw_raw = get_domain_keywords(
            target_domain=your_domain,
            location_name=location,
            limit=kw_limit,
            save=True
        )
        your_kw_list = _extract_domain_keywords(your_kw_raw)
        your_keywords = {k["keyword"] for k in your_kw_list}
        print(f"      Got {len(your_keywords)} of your keywords")
    else:
        print("\n[2/4] Skipping gap analysis (no your_domain provided)")

    # Step 3: Backlink profile
    print("\n[3/4] Pulling backlink profile...")
    backlink_profile = {}
    try:
        bl_raw = get_backlinks_summary(competitor_domain, save=True)
        backlink_profile = _extract_backlink_summary(bl_raw)
        print(f"      DR: {backlink_profile.get('rank', 'N/A')} | "
              f"RD: {backlink_profile.get('referring_domains', 'N/A')} | "
              f"Spam: {backlink_profile.get('spam_score', 'N/A')}")
    except Exception as e:
        print(f"      ⚠️  Backlink profile failed: {e}")

    # Step 4: Top pages
    print("\n[4/4] Pulling top pages...")
    top_pages = []
    try:
        pages_raw = get_domain_pages(competitor_domain, limit=pages_limit, save=True)
        top_pages = _extract_top_pages(pages_raw)
        print(f"      Got {len(top_pages)} top pages")
    except Exception as e:
        print(f"      ⚠️  Top pages failed: {e}")

    # Gap analysis
    gaps = []
    if your_domain and comp_keywords:
        gaps = [k for k in comp_keywords if k["keyword"] not in your_keywords]
        gaps.sort(key=lambda x: x.get("traffic_percent", 0), reverse=True)
        print(f"\n   Gap keywords (they rank, you don't): {len(gaps)}")

    # Build report
    report = _build_report(competitor_domain, your_domain, comp_keywords, top_pages,
                           backlink_profile, gaps)

    # Save report
    report_path = results_dir / f"{timestamp}__teardown__{competitor_domain.replace('.', '_')}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\n✅ Teardown report saved: {report_path.name}")

    full_result = {
        "competitor_domain": competitor_domain,
        "your_domain": your_domain,
        "competitor_keywords": comp_keywords[:50],
        "top_pages": top_pages,
        "backlink_profile": backlink_profile,
        "gaps": gaps[:50],
        "report": report,
        "report_path": str(report_path)
    }
    save_result(full_result, category="plays", operation="teardown", keyword=competitor_domain)

    return full_result


def _extract_domain_keywords(raw: Dict) -> List[Dict]:
    """Extract keyword rankings from Labs domain keywords response."""
    keywords = []
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    kd = item.get("keyword_data", {}) or {}
                    metrics = kd.get("keyword_info", {}) or {}
                    keywords.append({
                        "keyword": kd.get("keyword", item.get("keyword", "")),
                        "rank": item.get("ranked_serp_element", {}).get("serp_item", {}).get("rank_group", 0),
                        "volume": metrics.get("search_volume", 0) or 0,
                        "cpc": metrics.get("cpc", 0) or 0,
                        "traffic_percent": item.get("traffic_percent", 0) or 0,
                        "kd": kd.get("keyword_properties", {}).get("keyword_difficulty", 0) or 0,
                        "url": item.get("ranked_serp_element", {}).get("serp_item", {}).get("url", "")
                    })
    except Exception as e:
        print(f"      ⚠️  Keyword extraction error: {e}")
    return keywords


def _extract_backlink_summary(raw: Dict) -> Dict:
    """Extract key metrics from backlinks summary response."""
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                if isinstance(result, dict):
                    return {
                        "rank": result.get("rank", 0),
                        "backlinks": result.get("backlinks", 0),
                        "referring_domains": result.get("referring_domains", 0),
                        "referring_ips": result.get("referring_ips", 0),
                        "spam_score": result.get("spam_score", 0),
                        "is_lost": result.get("lost_backlinks", 0)
                    }
    except Exception:
        pass
    return {}


def _extract_top_pages(raw: Dict) -> List[Dict]:
    """Extract top pages from domain pages response."""
    pages = []
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if isinstance(item, dict):
                        pages.append({
                            "url": item.get("url", ""),
                            "backlinks": item.get("backlinks", 0),
                            "referring_domains": item.get("referring_domains", 0),
                            "rank": item.get("rank", 0)
                        })
    except Exception:
        pass
    return pages


def _build_report(competitor: str, your_domain: Optional[str], keywords: List[Dict],
                  pages: List[Dict], backlinks: Dict, gaps: List[Dict]) -> str:
    """Build a markdown teardown report."""
    lines = [
        f"# Competitor Teardown: {competitor}",
        f"",
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        f"",
    ]

    # Backlink profile
    if backlinks:
        lines.extend([
            f"## Backlink Profile",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Domain Rank | {backlinks.get('rank', 'N/A')} |",
            f"| Total Backlinks | {backlinks.get('backlinks', 'N/A'):,} |",
            f"| Referring Domains | {backlinks.get('referring_domains', 'N/A'):,} |",
            f"| Spam Score | {backlinks.get('spam_score', 'N/A')} |",
            f"",
        ])

    # Top keywords
    if keywords:
        lines.extend([
            f"## Top Keywords ({len(keywords)} total)",
            f"",
            f"| Keyword | Rank | Volume | CPC | KD | Traffic % |",
            f"|---------|------|--------|-----|----|-----------|",
        ])
        for kw in keywords[:20]:
            lines.append(
                f"| {kw['keyword']} | {kw.get('rank', '?')} | {kw.get('volume', 0):,} "
                f"| ${kw.get('cpc', 0):.2f} | {kw.get('kd', '?')} | {kw.get('traffic_percent', 0):.1f}% |"
            )
        lines.append("")

    # Top pages
    if pages:
        lines.extend([
            f"## Top Pages (by backlinks)",
            f"",
            f"| URL | Backlinks | Referring Domains |",
            f"|-----|-----------|------------------|",
        ])
        for page in pages[:10]:
            url = page.get("url", "")[:80]
            lines.append(
                f"| {url} | {page.get('backlinks', 0):,} | {page.get('referring_domains', 0):,} |"
            )
        lines.append("")

    # Gap analysis
    if gaps:
        lines.extend([
            f"## Gap Analysis vs {your_domain}",
            f"",
            f"Keywords {competitor} ranks for that {your_domain} doesn't:",
            f"",
            f"| Keyword | Their Rank | Volume | CPC |",
            f"|---------|-----------|--------|-----|",
        ])
        for kw in gaps[:20]:
            lines.append(
                f"| {kw['keyword']} | {kw.get('rank', '?')} "
                f"| {kw.get('volume', 0):,} | ${kw.get('cpc', 0):.2f} |"
            )
        lines.append("")
        lines.extend([
            f"## Quick Content Opportunities from Gap",
            f"",
            f"Top gap keywords by volume:",
        ])
        vol_sorted = sorted(gaps[:30], key=lambda x: x.get("volume", 0), reverse=True)
        for kw in vol_sorted[:10]:
            lines.append(f"- **{kw['keyword']}** - {kw.get('volume', 0):,} vol/mo, ${kw.get('cpc', 0):.2f} CPC")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    domain = sys.argv[1] if len(sys.argv) > 1 else "thespruce.com"
    your = sys.argv[2] if len(sys.argv) > 2 else None
    result = competitor_teardown(domain, your_domain=your)
    print(result["report"][:2000])
