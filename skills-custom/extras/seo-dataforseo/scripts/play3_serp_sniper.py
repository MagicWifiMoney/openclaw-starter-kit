"""
Play 3 - SERP Feature Sniper

Find featured snippet and People Also Ask (PAA) box opportunities.
These are the highest-CTR real estate in Google - target them deliberately.

Usage:
    from play3_serp_sniper import serp_feature_sniper
    result = serp_feature_sniper(["best dog beds", "how to crate train a dog"])
    result = serp_feature_sniper(keywords=None, domain="fifti-fifti.net", auto_discover=True)
"""
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from api.serp import get_google_serp, get_featured_snippet
from api.labs import get_keyword_ideas, get_domain_keywords
from core.storage import save_result
from config.settings import settings

# SERP feature types we care about
TARGET_FEATURES = {
    "featured_snippet",
    "people_also_ask",
    "knowledge_graph",
    "top_stories",
    "shopping",
    "local_pack",
    "video_carousel",
    "related_searches"
}

# Keywords that commonly trigger featured snippets
SNIPPET_TRIGGERS = ["how to", "what is", "how do", "why does", "best way to", "steps to",
                    "difference between", "vs", "definition", "explain", "guide to",
                    "types of", "benefits of", "how long", "how much", "what are"]


def serp_feature_sniper(
    keywords: Optional[List[str]] = None,
    domain: Optional[str] = None,
    auto_discover: bool = False,
    location_name: str = None,
    limit: int = 50,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Find featured snippet and PAA box opportunities in a keyword list.

    Modes:
    1. keywords list: analyze given list for features
    2. domain + auto_discover: pull domain's keywords + find feature gaps
    3. domain only: analyze top domain keywords for feature opportunities

    Args:
        keywords: List of keywords to analyze
        domain: Your domain (for auto-discovery mode)
        auto_discover: Pull domain's existing keywords and find snippet opportunities
        location_name: Target location (default: United States)
        limit: Max keywords to process (cost safeguard)
        dry_run: Estimate cost without hitting API

    Returns:
        Dict with:
            - snippet_opportunities: keywords with featured snippets to steal
            - paa_opportunities: keywords with PAA boxes
            - you_own: features you currently own (if domain provided)
            - report: markdown opportunity report

    Cost estimate: ~$0.01-0.05 per keyword checked (SERP advanced)

    Example:
        >>> result = serp_feature_sniper(["how to organize bathroom", "best bathroom decor"])
        >>> result = serp_feature_sniper(domain="fifti-fifti.net", auto_discover=True, limit=20)
    """
    location = location_name or settings.DEFAULT_LOCATION_NAME
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n🎯 SERP Feature Sniper")
    if domain:
        print(f"   Domain: {domain}")
    if keywords:
        print(f"   Keywords: {len(keywords)} provided")

    results_dir = Path(__file__).parent / "results" / "plays"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Build keyword list
    if not keywords:
        if domain:
            print(f"\n[1/3] Discovering keywords from {domain}...")
            try:
                kw_raw = get_domain_keywords(
                    target_domain=domain,
                    location_name=location,
                    limit=min(limit * 2, 200),
                    save=True
                )
                keywords = _extract_domain_kws(kw_raw)
                print(f"      Got {len(keywords)} domain keywords")
            except Exception as e:
                print(f"      ⚠️  Could not get domain keywords: {e}")
                keywords = []

            if auto_discover and len(keywords) < 10:
                print(f"      Expanding with keyword ideas...")
                domain_name = domain.replace("www.", "").split(".")[0].replace("-", " ")
                try:
                    ideas_raw = get_keyword_ideas(keywords=[domain_name], location_name=location, limit=100, save=True)
                    extra = _extract_ideas_kws(ideas_raw)
                    keywords.extend(extra[:50])
                    print(f"      Total keywords: {len(keywords)}")
                except Exception as e:
                    print(f"      ⚠️  Ideas expansion failed: {e}")
        else:
            print("ERROR: Provide either keywords list or domain")
            return {"error": "No keywords or domain provided"}

    # Prioritize snippet-trigger keywords
    keywords = _prioritize_snippet_triggers(keywords)[:min(limit, 100)]

    if dry_run:
        estimated_cost = len(keywords) * 0.01
        print(f"\n[DRY RUN] Would check {len(keywords)} keywords. Estimated cost: ~${estimated_cost:.2f}")
        return {"dry_run": True, "keywords_to_check": len(keywords), "estimated_cost": estimated_cost}

    # Step 2: Check SERP features for each keyword
    print(f"\n[2/3] Scanning {len(keywords)} keywords for SERP features...")
    snippet_opportunities = []
    paa_opportunities = []
    you_own = []
    all_features_found = []

    for i, kw in enumerate(keywords):
        print(f"      [{i+1}/{len(keywords)}] {kw}...")
        try:
            serp_raw = get_featured_snippet(kw, location_name=location, save=False)
            features = _extract_serp_features(serp_raw, kw, domain)
            all_features_found.append(features)

            if features.get("has_featured_snippet"):
                opportunity = {
                    "keyword": kw,
                    "feature_type": "featured_snippet",
                    "snippet_owner": features.get("snippet_owner", "unknown"),
                    "snippet_type": features.get("snippet_type", "paragraph"),
                    "your_rank": features.get("your_rank"),
                    "difficulty": features.get("snippet_difficulty", "medium"),
                    "opportunity_score": _calc_opportunity_score(features)
                }
                if domain and features.get("snippet_owner_domain") == domain:
                    you_own.append({**opportunity, "you_own": True})
                else:
                    snippet_opportunities.append(opportunity)

            if features.get("has_paa"):
                paa_entry = {
                    "keyword": kw,
                    "feature_type": "people_also_ask",
                    "paa_questions": features.get("paa_questions", [])[:5],
                    "your_rank": features.get("your_rank"),
                    "opportunity_score": _calc_opportunity_score(features) * 0.8
                }
                paa_opportunities.append(paa_entry)

        except Exception as e:
            print(f"         ⚠️  Failed: {e}")

    # Step 3: Generate report
    print(f"\n[3/3] Building opportunity report...")
    snippet_opportunities.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
    paa_opportunities.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)

    report = _generate_sniper_report(domain, snippet_opportunities, paa_opportunities, you_own)

    # Save CSV
    csv_path = results_dir / f"{timestamp}__serp_sniper__{(domain or 'keywords').replace('.', '_')}.csv"
    _save_sniper_csv(snippet_opportunities + paa_opportunities, csv_path)

    full_result = {
        "domain": domain,
        "keywords_checked": len(keywords),
        "snippet_opportunities": snippet_opportunities[:20],
        "paa_opportunities": paa_opportunities[:20],
        "you_own": you_own,
        "total_snippet_opps": len(snippet_opportunities),
        "total_paa_opps": len(paa_opportunities),
        "csv_path": str(csv_path),
        "report": report
    }
    save_result(full_result, category="plays", operation="serp_sniper", keyword=domain or "keywords")

    print(f"\n✅ Found {len(snippet_opportunities)} snippet opportunities + {len(paa_opportunities)} PAA opportunities")
    print(report[:600])
    return full_result


def _extract_domain_kws(raw: Dict) -> List[str]:
    """Extract keywords from domain keywords response."""
    keywords = []
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    kw = item.get("keyword", "")
                    if kw and kw not in keywords:
                        keywords.append(kw)
    except Exception:
        pass
    return keywords


def _extract_ideas_kws(raw: Dict) -> List[str]:
    """Extract keywords from ideas response."""
    keywords = []
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    kw = item.get("keyword", "")
                    if kw and kw not in keywords:
                        keywords.append(kw)
    except Exception:
        pass
    return keywords


def _prioritize_snippet_triggers(keywords: List[str]) -> List[str]:
    """Sort keywords so snippet-trigger phrases come first."""
    trigger_kws = []
    other_kws = []
    for kw in keywords:
        kw_lower = kw.lower()
        if any(trigger in kw_lower for trigger in SNIPPET_TRIGGERS):
            trigger_kws.append(kw)
        else:
            other_kws.append(kw)
    return trigger_kws + other_kws


def _extract_serp_features(raw: Dict, keyword: str, domain: Optional[str]) -> Dict:
    """Extract SERP feature data from API response."""
    result = {
        "keyword": keyword,
        "has_featured_snippet": False,
        "has_paa": False,
        "snippet_owner": None,
        "snippet_owner_domain": None,
        "snippet_type": None,
        "paa_questions": [],
        "your_rank": None,
        "features_present": []
    }

    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for task_result in task.get("result", []) or []:
                items = task_result.get("items", []) or []
                for item in items:
                    item_type = item.get("type", "")

                    # Featured snippet
                    if item_type == "featured_snippet":
                        result["has_featured_snippet"] = True
                        result["snippet_type"] = item.get("featured_snippet_type", "paragraph")
                        url = item.get("url", "") or ""
                        result["snippet_owner"] = item.get("domain", url.split("/")[2] if "//" in url else url)
                        result["snippet_owner_domain"] = result["snippet_owner"]
                        result["features_present"].append("featured_snippet")

                    # PAA (People Also Ask)
                    elif item_type == "people_also_ask":
                        result["has_paa"] = True
                        result["features_present"].append("people_also_ask")
                        for paa_item in item.get("items", []) or []:
                            q = paa_item.get("question", "") or paa_item.get("title", "")
                            if q:
                                result["paa_questions"].append(q)

                    # Your rank
                    elif item_type == "organic" and domain:
                        item_domain = item.get("domain", "")
                        if domain in item_domain or item_domain in domain:
                            rank = item.get("rank_absolute", 0)
                            if result["your_rank"] is None or rank < result["your_rank"]:
                                result["your_rank"] = rank

                    # Track all features
                    if item_type in TARGET_FEATURES:
                        if item_type not in result["features_present"]:
                            result["features_present"].append(item_type)

    except Exception as e:
        print(f"         ⚠️  Feature extraction error: {e}")

    return result


def _calc_opportunity_score(features: Dict) -> float:
    """Score the opportunity based on available signals."""
    score = 50.0  # Base score

    # You're already ranking? Higher chance of winning snippet
    your_rank = features.get("your_rank")
    if your_rank:
        if your_rank <= 3:
            score += 40
        elif your_rank <= 5:
            score += 25
        elif your_rank <= 10:
            score += 15

    # Snippet type matters
    snippet_type = features.get("snippet_type", "")
    if snippet_type == "list":
        score += 10  # Lists are easier to structure-optimize
    elif snippet_type == "table":
        score += 5

    return min(score, 100)


def _save_sniper_csv(opportunities: List[Dict], path: Path):
    """Save opportunities to CSV."""
    if not opportunities:
        return
    fieldnames = ["keyword", "feature_type", "snippet_owner", "snippet_type",
                  "your_rank", "opportunity_score", "paa_questions"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for opp in opportunities:
            row = opp.copy()
            if isinstance(row.get("paa_questions"), list):
                row["paa_questions"] = " | ".join(row["paa_questions"][:3])
            writer.writerow(row)


def _generate_sniper_report(
    domain: Optional[str],
    snippet_opps: List[Dict],
    paa_opps: List[Dict],
    you_own: List[Dict]
) -> str:
    """Generate markdown SERP sniper report."""
    lines = [
        f"# SERP Feature Sniper Report",
        f"" ,
    ]
    if domain:
        lines.append(f"**Domain:** {domain}")
    lines.extend([
        f"**Featured Snippet Opportunities:** {len(snippet_opps)}",
        f"**PAA Opportunities:** {len(paa_opps)}",
        f"**Features You Currently Own:** {len(you_own)}",
        f"",
        f"---",
        f"",
        f"## Top Featured Snippet Opportunities",
        f"*(These keywords have a snippet - you can write structured content to steal it)*",
        f"",
        f"| Keyword | Current Owner | Snippet Type | Your Rank | Opp Score |",
        f"|---------|--------------|--------------|-----------|-----------|",
    ])

    for opp in snippet_opps[:15]:
        lines.append(
            f"| {opp['keyword']} | {opp.get('snippet_owner', 'unknown')[:30]} "
            f"| {opp.get('snippet_type', 'paragraph')} | #{opp.get('your_rank', '-')} "
            f"| {opp.get('opportunity_score', 0):.0f} |"
        )

    lines.extend([
        f"",
        f"## Top PAA Opportunities",
        f"*(Answer these questions to appear in PAA boxes)*",
        f"",
    ])

    for opp in paa_opps[:10]:
        lines.append(f"**{opp['keyword']}** (PAA rank: #{opp.get('your_rank', '-')})")
        for q in opp.get("paa_questions", [])[:3]:
            lines.append(f"  - {q}")
        lines.append("")

    if you_own:
        lines.extend([
            f"## Features You Currently Own (Defend These!)",
            f"",
        ])
        for owned in you_own:
            lines.append(f"- **{owned['keyword']}** - {owned.get('snippet_type', 'snippet')} at rank #{owned.get('your_rank', '-')}")

    lines.extend([
        f"",
        f"## How to Win Featured Snippets",
        f"",
        f"1. **Answer the query directly** in the first 40-50 words of your page",
        f"2. **Use structured formats** - numbered lists for 'how to', tables for comparisons",
        f"3. **Target position 1-5 first** - snippets almost always go to top 5 rankers",
        f"4. **Use the exact query** as an H2 header, then answer below",
        f"5. **For PAA**: Add FAQ sections with verbatim question as H3 + 40-60 word answer",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Support: python play3_serp_sniper.py "keyword1" "keyword2"
        # or: python play3_serp_sniper.py --domain example.com
        if sys.argv[1] == "--domain":
            domain = sys.argv[2] if len(sys.argv) > 2 else "example.com"
            result = serp_feature_sniper(domain=domain, auto_discover=True, limit=20)
        else:
            keywords = sys.argv[1:]
            result = serp_feature_sniper(keywords=keywords)
    else:
        print("Usage: python play3_serp_sniper.py 'keyword1' 'keyword2' ...")
        print("       python play3_serp_sniper.py --domain example.com")
        sys.exit(1)

    if not result.get("dry_run") and not result.get("error"):
        print(result.get("report", ""))
