"""
Play 1 - Affiliate Keyword Miner

Find keywords worth writing affiliate content for.
Filters by CPC floor + KD ceiling, then checks SERP for affiliate signals.

Usage:
    from play1_affiliate_kw import affiliate_keyword_miner
    result = affiliate_keyword_miner("home organization", cpc_floor=1.0, kd_ceiling=40)
"""
import sys
import csv
import json
import math
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from api.labs import get_keyword_ideas, get_bulk_keyword_difficulty
from api.serp import get_google_serp
from api.trends import get_trends_explore
from core.storage import save_result
from config.settings import settings

# Affiliate network signal domains - if these appear in top 10, it's a proven play
AFFILIATE_SIGNALS = [
    "amazon.com", "rakuten.com", "shareasale.com", "cj.com", "impact.com",
    "avantlink.com", "bestbuy.com", "target.com", "walmart.com", "wayfair.com",
    "homedepot.com", "lowes.com", "etsy.com", "chewy.com", "petco.com",
    "petsmart.com", "kohls.com", "macys.com", "overstock.com"
]

# Review/comparison sites that signal affiliate opportunity
REVIEW_SIGNALS = [
    "thewirecutter.com", "tomsguide.com", "pcmag.com", "rtings.com",
    "goodhousekeeping.com", "bhg.com", "realsimple.com", "hgtv.com",
    "clevercreations.com", "thespruce.com", "bobvila.com"
]


def affiliate_keyword_miner(
    topic: str,
    cpc_floor: float = 1.0,
    kd_ceiling: int = 40,
    location_name: str = None,
    limit: int = 200,
    check_serp: bool = True
) -> Dict[str, Any]:
    """
    Find affiliate-worthy keywords for a niche.

    Args:
        topic: Niche or seed keyword (e.g. "home organization", "dog toys")
        cpc_floor: Minimum CPC in USD (default $1.00)
        kd_ceiling: Maximum keyword difficulty (default 40)
        location_name: Target location (default: United States)
        limit: Max keyword ideas to fetch (default 200)
        check_serp: Whether to check SERP for affiliate signals (adds cost + time)

    Returns:
        Dict with:
            - filtered_keywords: list of qualifying keywords with scores
            - top_20: top 20 by affiliate viability score
            - csv_path: path to saved CSV
            - summary: markdown summary text

    Cost estimate: ~$0.03-0.10 depending on limit and SERP checks

    Example:
        >>> result = affiliate_keyword_miner("home organization", cpc_floor=1.0, kd_ceiling=40)
        >>> result = affiliate_keyword_miner("dog bathroom decor", cpc_floor=0.50, kd_ceiling=50)
    """
    location = location_name or settings.DEFAULT_LOCATION_NAME
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n🎯 Affiliate Keyword Miner: '{topic}'")
    print(f"   Filters: CPC >= ${cpc_floor}, KD <= {kd_ceiling}")

    results_dir = Path(__file__).parent / "results" / "plays"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Get keyword ideas
    print("\n[1/4] Fetching keyword ideas...")
    ideas_raw = get_keyword_ideas(
        keywords=[topic],
        location_name=location,
        limit=min(limit, 1000),
        save=True
    )

    # Extract keyword items from nested response
    keywords = _extract_keywords_from_ideas(ideas_raw)
    print(f"      Got {len(keywords)} keyword ideas")

    # Step 2: Filter by CPC + volume (KD comes from overview data)
    print(f"\n[2/4] Filtering by CPC >= ${cpc_floor}...")
    filtered = []
    for kw in keywords:
        # Nested structure: keyword_info.cpc, keyword_info.search_volume, keyword_properties.keyword_difficulty
        ki = kw.get("keyword_info", {}) or {}
        kp = kw.get("keyword_properties", {}) or {}
        cpc = float(ki.get("cpc", 0) or kw.get("cpc", 0) or 0)
        volume = int(ki.get("search_volume", 0) or kw.get("search_volume", 0) or 0)
        kd = int(kp.get("keyword_difficulty", kw.get("keyword_difficulty", 100)) or 0)
        if kd == 0 and volume > 0:
            kd = 20  # Default moderate KD if missing

        if cpc >= cpc_floor and volume > 0 and kd <= kd_ceiling:
            # Affiliate viability score: volume * CPC / max(KD, 1)
            avs = (volume * cpc) / max(kd, 1)
            filtered.append({
                "keyword": kw.get("keyword", ""),
                "volume": volume,
                "cpc": round(cpc, 2),
                "kd": kd,
                "avs": round(avs, 2),
                "competition": ki.get("competition_level", kw.get("competition", "")),
                "affiliate_signals": 0,
                "serp_checked": False
            })

    filtered.sort(key=lambda x: x["avs"], reverse=True)
    print(f"      {len(filtered)} keywords pass CPC + KD filters")

    # Step 3: Check SERP for top candidates for affiliate signals
    if check_serp and filtered:
        top_candidates = filtered[:15]  # Check top 15 to save cost
        print(f"\n[3/4] Checking SERP for affiliate signals (top {len(top_candidates)})...")

        for i, kw_data in enumerate(top_candidates):
            kw = kw_data["keyword"]
            print(f"      [{i+1}/{len(top_candidates)}] {kw}...")
            try:
                serp_raw = get_google_serp(kw, location_name=location, depth=10, save=False)
                signal_count, signal_domains = _count_affiliate_signals(serp_raw)
                kw_data["affiliate_signals"] = signal_count
                kw_data["signal_domains"] = signal_domains
                kw_data["serp_checked"] = True
                if signal_count > 0:
                    print(f"         ✅ {signal_count} affiliate signals: {signal_domains[:2]}")
            except Exception as e:
                print(f"         ⚠️  SERP check failed: {e}")
    else:
        print("\n[3/4] Skipping SERP check (check_serp=False)")

    # Step 4: Get trend data for top 5 (5 per Trends task)
    top5_kws = [k["keyword"] for k in filtered[:5]]
    trend_data = {}
    if top5_kws:
        print(f"\n[4/4] Getting trend data for top 5 keywords...")
        try:
            trends_raw = get_trends_explore(keywords=top5_kws, location_name=location, save=True)
            trend_data = _extract_trend_data(trends_raw)
        except Exception as e:
            print(f"      ⚠️  Trends failed: {e}")

    # Re-sort including affiliate signals boost
    for kw_data in filtered:
        if kw_data.get("affiliate_signals", 0) > 0:
            kw_data["avs"] = kw_data["avs"] * (1 + 0.2 * kw_data["affiliate_signals"])
        if kw_data["keyword"] in trend_data:
            kw_data["trend_peak"] = trend_data[kw_data["keyword"]]

    filtered.sort(key=lambda x: x["avs"], reverse=True)
    top_20 = filtered[:20]

    # Save CSV
    csv_path = results_dir / f"{timestamp}__affiliate_keywords__{topic.replace(' ', '_')}.csv"
    _save_csv(top_20, csv_path)
    print(f"\n✅ Saved CSV: {csv_path.name}")

    # Generate summary
    summary = _generate_summary(topic, top_20, cpc_floor, kd_ceiling)

    # Save JSON result
    full_result = {
        "topic": topic,
        "filters": {"cpc_floor": cpc_floor, "kd_ceiling": kd_ceiling},
        "total_ideas": len(keywords),
        "total_filtered": len(filtered),
        "top_20": top_20,
        "csv_path": str(csv_path),
        "summary": summary
    }
    save_result(full_result, category="plays", operation="affiliate_kw", keyword=topic)

    print(summary[:500])
    return full_result


def _extract_keywords_from_ideas(raw: Dict) -> List[Dict]:
    """Extract keyword items from Labs API response."""
    keywords = []
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            for result in task.get("result", []) or []:
                if not isinstance(result, dict):
                    continue
                for item in result.get("items", []) or []:
                    if isinstance(item, dict):
                        keywords.append(item)
    except Exception as e:
        print(f"      ⚠️  Could not extract keywords: {e}")
    return keywords


def _count_affiliate_signals(serp_raw: Dict) -> tuple:
    """Count affiliate signals in top 10 SERP results."""
    count = 0
    found_domains = []
    try:
        tasks = serp_raw.get("tasks", []) if isinstance(serp_raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    url = item.get("url", "") or ""
                    domain = item.get("domain", "") or ""
                    rank = item.get("rank_group", 99) or 99
                    if rank > 10:
                        continue
                    for signal in AFFILIATE_SIGNALS + REVIEW_SIGNALS:
                        if signal in url or signal in domain:
                            count += 1
                            if signal not in found_domains:
                                found_domains.append(signal)
    except Exception:
        pass
    return count, found_domains


def _extract_trend_data(trends_raw: Dict) -> Dict:
    """Extract trend peak month per keyword."""
    trend_map = {}
    try:
        tasks = trends_raw.get("tasks", []) if isinstance(trends_raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                kw = result.get("keyword", "")
                data = result.get("data", []) or []
                if data and kw:
                    peak = max(data, key=lambda x: x.get("values", [0])[0] if x.get("values") else 0)
                    trend_map[kw] = peak.get("date_to", "")[:7]
    except Exception:
        pass
    return trend_map


def _save_csv(keywords: List[Dict], path: Path):
    """Save keyword list to CSV."""
    if not keywords:
        return
    fieldnames = ["keyword", "volume", "cpc", "kd", "avs", "competition",
                  "affiliate_signals", "signal_domains", "trend_peak"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(keywords)


def _generate_summary(topic: str, top_20: List[Dict], cpc_floor: float, kd_ceiling: int) -> str:
    """Generate markdown summary."""
    lines = [
        f"# Affiliate Keyword Miner: {topic}",
        f"",
        f"**Filters:** CPC >= ${cpc_floor} | KD <= {kd_ceiling}",
        f"**Top results:** {len(top_20)} keywords",
        f"",
        f"## Top 20 by Affiliate Viability Score (AVS = Volume x CPC / KD)",
        f"",
        f"| # | Keyword | Volume | CPC | KD | AVS | Affiliate Signals |",
        f"|---|---------|--------|-----|----|-----|-------------------|",
    ]
    for i, kw in enumerate(top_20, 1):
        signals = kw.get("affiliate_signals", "-")
        lines.append(
            f"| {i} | {kw['keyword']} | {kw['volume']:,} | ${kw['cpc']} "
            f"| {kw['kd']} | {kw['avs']:.0f} | {signals} |"
        )

    lines.extend([
        f"",
        f"## Quick Wins (KD <= 20, CPC >= $1)",
        f"",
    ])
    quick_wins = [k for k in top_20 if k["kd"] <= 20 and k["cpc"] >= 1.0]
    for kw in quick_wins[:5]:
        lines.append(f"- **{kw['keyword']}** - {kw['volume']:,} vol, ${kw['cpc']} CPC, KD {kw['kd']}")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "home organization"
    cpc = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    kd = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    result = affiliate_keyword_miner(topic, cpc_floor=cpc, kd_ceiling=kd)
    print(result["summary"])
