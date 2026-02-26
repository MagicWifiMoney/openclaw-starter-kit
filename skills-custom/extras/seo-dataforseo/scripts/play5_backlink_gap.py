"""
Play 5 - Backlink Gap Finder

Find domains linking to competitors but NOT to you.
These are your highest-priority link-building targets - they've already
decided to link to sites like yours. Just give them a reason to link to you.

Usage:
    from play5_backlink_gap import backlink_gap_finder
    result = backlink_gap_finder("mysite.com", "competitor.com")
    result = backlink_gap_finder("fifti-fifti.net", "overstock.com", min_dr=20)
"""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))

from api.backlinks import get_bulk_backlinks_summary, get_referring_domains, get_backlinks_summary, get_domain_intersection
from core.storage import save_result
from config.settings import settings

MIN_DR_THRESHOLD = 10

def _get_referring_domain_set(domain: str, limit: int = 500) -> Dict[str, Dict]:
    """Get all referring domains for a target, return as {domain: data} dict."""
    try:
        result = get_referring_domains(domain, limit=limit)
        if not result:
            return {}
        domains = {}
        tasks = result.get("tasks", []) if isinstance(result, dict) else []
        for task in tasks:
            for res in task.get("result", []) or []:
                for item in (res.get("items", []) or []):
                    rd = item.get("domain", "") or item.get("referring_domain", "")
                    if rd:
                        domains[rd] = {
                            "dr": item.get("rank", 0),
                            "backlinks_to_target": item.get("backlinks", 1),
                        }
        return domains
    except Exception as e:
        print(f"  Error fetching referring domains for {domain}: {e}")
        return {}


def backlink_gap_finder(
    your_domain: str,
    competitor_domain: str,
    min_dr: int = MIN_DR_THRESHOLD,
    limit: int = 500,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Find domains linking to competitor but not you.

    Args:
        your_domain: Your site (e.g. "fifti-fifti.net")
        competitor_domain: Their site (e.g. "overstock.com")
        min_dr: Minimum domain rank to include in gap list
        limit: Max referring domains to fetch per site
        dry_run: Estimate cost without hitting API

    Returns:
        Dict with gap_domains, overlap, profile comparison, and report

    Cost estimate: ~$0.04-0.08 per competitor comparison
    """
    settings.validate()
    your_domain = your_domain.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
    comp_domain = competitor_domain.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")

    print(f"\n🔗 Backlink Gap: {your_domain} vs {comp_domain}")

    if dry_run:
        print(f"[DRY RUN] Would fetch RDs for 2 domains. Est. cost: ~$0.04-0.08")
        return {"dry_run": True, "estimated_cost": 0.06}

    print(f"Fetching referring domains...")
    your_rds = _get_referring_domain_set(your_domain, limit=limit)
    comp_rds = _get_referring_domain_set(comp_domain, limit=limit)

    print(f"  {your_domain}: {len(your_rds)} referring domains")
    print(f"  {comp_domain}: {len(comp_rds)} referring domains")

    your_set = set(your_rds.keys())
    comp_set = set(comp_rds.keys())

    gap_domains_raw = comp_set - your_set
    overlap_raw = comp_set & your_set
    unique_yours_raw = your_set - comp_set

    # Filter by DR and sort
    gap_domains = []
    for d in gap_domains_raw:
        dr = comp_rds[d].get("dr", 0)
        if dr >= min_dr:
            gap_domains.append({
                "domain": d,
                "dr": dr,
                "links_to_competitor": comp_rds[d].get("backlinks_to_target", 1),
                "outreach_priority": "high" if dr >= 40 else "medium" if dr >= 20 else "low",
            })

    gap_domains.sort(key=lambda x: x["dr"], reverse=True)

    overlap = [{"domain": d, "dr": comp_rds[d].get("dr", 0)} for d in overlap_raw
               if comp_rds[d].get("dr", 0) >= min_dr]
    overlap.sort(key=lambda x: x["dr"], reverse=True)

    # Save CSV
    results_dir = Path(__file__).parent / "results" / "plays"
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = results_dir / f"{timestamp}__backlink_gap__{your_domain.replace('.','_')}_vs_{comp_domain.replace('.','_')}.csv"
    if gap_domains:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["domain", "dr", "links_to_competitor", "outreach_priority"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(gap_domains)

    result = {
        "status": "success",
        "your_domain": your_domain,
        "competitor_domain": comp_domain,
        "your_total_rds": len(your_rds),
        "competitor_total_rds": len(comp_rds),
        "gap_count": len(gap_domains),
        "overlap_count": len(overlap),
        "unique_to_you_count": len(unique_yours_raw),
        "gap_domains": gap_domains,
        "overlap_domains": overlap[:50],
        "high_priority_count": sum(1 for d in gap_domains if d["outreach_priority"] == "high"),
        "csv_path": str(csv_path),
        "timestamp": datetime.now().isoformat(),
    }

    save_result(result, category="backlinks", operation="gap_finder",
                keyword=f"{your_domain}_vs_{comp_domain}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"BACKLINK GAP: {your_domain} vs {comp_domain}")
    print(f"{'='*60}")
    print(f"Competitor referring domains: {len(comp_rds)}")
    print(f"Your referring domains:       {len(your_rds)}")
    print(f"GAP (link them, not you):     {len(gap_domains)} (DR>={min_dr})")
    print(f"  High priority (DR>=40):     {result['high_priority_count']}")
    print(f"Overlap (link both):          {len(overlap)}")
    print()
    print("TOP 20 GAP OPPORTUNITIES:")
    for d in gap_domains[:20]:
        icon = "🔴" if d["outreach_priority"] == "high" else "🟡" if d["outreach_priority"] == "medium" else "⚪"
        print(f"  {icon} DR {d['dr']:3} | {d['domain']}")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python play5_backlink_gap.py your_domain.com competitor.com [min_dr]")
        sys.exit(1)
    your_domain = sys.argv[1]
    competitor = sys.argv[2]
    min_dr = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    backlink_gap_finder(your_domain, competitor, min_dr=min_dr)
