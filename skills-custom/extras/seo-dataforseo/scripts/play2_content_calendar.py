"""
Play 2 - Content Calendar Builder

Build a 30-day content calendar from keyword clusters for any domain.
Groups keywords by topic cluster, assigns content types (pillar/hub/spoke),
and schedules publishing dates spread across 30 days.

Usage:
    from play2_content_calendar import content_calendar_builder
    result = content_calendar_builder("fifti-fifti.net")
    result = content_calendar_builder("mplsvegan.com", seed_topics=["vegan recipes", "plant based"])
"""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from api.labs import get_keyword_ideas, get_bulk_keyword_difficulty, get_search_intent, get_keywords_for_site
from api.trends import get_trends_explore
from core.storage import save_result
from config.settings import settings

# Content type thresholds
PILLAR_VOLUME = 5000    # Broad/hub topic (1000+ volume, informational intent)
SPOKE_KD_MAX = 35       # Spoke articles - keep it achievable


def content_calendar_builder(
    domain: str,
    seed_topics: Optional[List[str]] = None,
    days: int = 30,
    location_name: str = None,
    ideas_per_topic: int = 100,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Build a 30-day content calendar from keyword clusters.

    Args:
        domain: Your site's domain (e.g. "fifti-fifti.net") - used to seed topic ideas
        seed_topics: Optional list of seed keywords/topics to expand
        days: Calendar length in days (default 30)
        location_name: Target location (default: United States)
        ideas_per_topic: Keyword ideas to pull per seed topic (default 100)
        dry_run: Print plan without saving if True

    Returns:
        Dict with:
            - calendar: list of {date, slug, title, type, keyword, volume, kd, intent}
            - clusters: keyword clusters by topic
            - csv_path: path to saved CSV
            - summary: markdown calendar table

    Cost estimate: ~$0.05-0.15 depending on number of seed topics

    Example:
        >>> result = content_calendar_builder("fifti-fifti.net")
        >>> result = content_calendar_builder("mplsvegan.com", seed_topics=["vegan recipes", "vegan restaurants"])
    """
    location = location_name or settings.DEFAULT_LOCATION_NAME
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n📅 Content Calendar Builder: {domain}")
    print(f"   Building {days}-day calendar")

    results_dir = Path(__file__).parent / "results" / "plays"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Get seed topics from domain if not provided
    if not seed_topics:
        print("\n[1/4] Discovering site topics from domain rankings...")
        try:
            site_kws_raw = get_keywords_for_site(
                target=domain,
                location_name=location,
                limit=50,
                save=True
            )
            seed_topics = _extract_top_topics(site_kws_raw)
            print(f"      Discovered {len(seed_topics)} seed topics: {seed_topics[:3]}...")
        except Exception as e:
            print(f"      ⚠️  Could not pull site keywords: {e}")
            seed_topics = [domain.replace(".net", "").replace(".com", "").replace(".org", "").replace("-", " ")]
            print(f"      Falling back to domain name: {seed_topics}")
    else:
        print(f"\n[1/4] Using provided seed topics: {seed_topics[:3]}...")

    # Step 2: Expand each topic into keyword ideas
    print(f"\n[2/4] Expanding {len(seed_topics[:5])} topics into keyword ideas...")
    all_keywords = []
    for topic in seed_topics[:5]:  # Cap at 5 topics to manage cost
        try:
            ideas_raw = get_keyword_ideas(
                keywords=[topic],
                location_name=location,
                limit=ideas_per_topic,
                save=True
            )
            kws = _extract_keyword_items(ideas_raw)
            for kw in kws:
                kw["seed_topic"] = topic
            all_keywords.extend(kws)
            print(f"      '{topic}' → {len(kws)} ideas")
        except Exception as e:
            print(f"      ⚠️  Failed for '{topic}': {e}")

    # Deduplicate
    seen = set()
    unique_keywords = []
    for kw in all_keywords:
        if kw.get("keyword") and kw["keyword"] not in seen:
            seen.add(kw["keyword"])
            unique_keywords.append(kw)

    print(f"      Total unique keywords: {len(unique_keywords)}")

    if dry_run:
        print(f"\n[DRY RUN] Would process {len(unique_keywords)} keywords into {days}-day calendar")
        return {"dry_run": True, "keyword_count": len(unique_keywords)}

    # Step 3: Get search intent for top candidates
    top_candidates = _filter_calendar_candidates(unique_keywords, limit=60)
    kw_texts = [k["keyword"] for k in top_candidates]

    print(f"\n[3/4] Getting search intent for {len(kw_texts)} candidates...")
    intent_map = {}
    batch_size = 700
    for i in range(0, len(kw_texts), batch_size):
        batch = kw_texts[i:i+batch_size]
        try:
            intent_raw = get_search_intent(keywords=batch, location_name=location, save=False)
            intent_map.update(_extract_intent_map(intent_raw))
        except Exception as e:
            print(f"      ⚠️  Intent batch failed: {e}")

    # Step 4: Cluster and assign content types
    print(f"\n[4/4] Building {days}-day calendar from clusters...")
    clusters = _cluster_keywords(top_candidates, intent_map)
    calendar = _build_calendar(clusters, days=days, start_date=datetime.now())

    # Save CSV
    csv_path = results_dir / f"{timestamp}__content_calendar__{domain.replace('.', '_')}.csv"
    _save_calendar_csv(calendar, csv_path)

    # Generate summary
    summary = _generate_calendar_summary(domain, calendar, days)

    full_result = {
        "domain": domain,
        "days": days,
        "total_posts": len(calendar),
        "calendar": calendar,
        "clusters": {k: len(v) for k, v in clusters.items()},
        "csv_path": str(csv_path),
        "summary": summary
    }
    save_result(full_result, category="plays", operation="content_calendar", keyword=domain)

    print(f"\n✅ Calendar built: {len(calendar)} posts over {days} days")
    print(f"   Saved: {csv_path.name}")
    return full_result


def _extract_top_topics(raw: Dict) -> List[str]:
    """Extract top-level topics from domain keywords."""
    topics = []
    stop_words = {"the", "a", "an", "and", "or", "for", "of", "in", "on", "to", "how", "what", "is", "are"}
    word_freq = defaultdict(int)
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    kw = item.get("keyword", "")
                    if kw:
                        words = [w.lower() for w in kw.split() if w.lower() not in stop_words and len(w) > 3]
                        for w in words:
                            word_freq[w] += 1
    except Exception:
        pass

    # Get top 5 most common words as seed topics
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:5]] or ["content ideas"]


def _extract_keyword_items(raw: Dict) -> List[Dict]:
    """Extract keyword items from Labs API response."""
    keywords = []
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    if isinstance(item, dict) and item.get("keyword"):
                        ki = item.get("keyword_info", {}) or {}
                        kp = item.get("keyword_properties", {}) or {}
                        keywords.append({
                            "keyword": item["keyword"],
                            "volume": int(ki.get("search_volume", 0) or 0),
                            "cpc": float(ki.get("cpc", 0) or 0),
                            "kd": int(kp.get("keyword_difficulty", 50) or 50),
                            "competition": ki.get("competition_level", "medium")
                        })
    except Exception as e:
        print(f"      ⚠️  Could not extract keywords: {e}")
    return keywords


def _filter_calendar_candidates(keywords: List[Dict], limit: int = 60) -> List[Dict]:
    """Filter and rank keywords for calendar candidacy."""
    # Remove duplicates, require at least some volume
    filtered = [k for k in keywords if k.get("volume", 0) > 50]

    # Score: volume * (1 / max(kd, 1)) - balance traffic potential vs difficulty
    for kw in filtered:
        kd = kw.get("kd", 50) or 50
        vol = kw.get("volume", 0)
        kw["calendar_score"] = (vol ** 0.5) / max(kd / 10, 1)

    filtered.sort(key=lambda x: x.get("calendar_score", 0), reverse=True)
    return filtered[:limit]


def _extract_intent_map(raw: Dict) -> Dict[str, str]:
    """Build keyword -> intent mapping from intent API response."""
    intent_map = {}
    try:
        tasks = raw.get("tasks", []) if isinstance(raw, dict) else []
        for task in tasks:
            for result in task.get("result", []) or []:
                for item in result.get("items", []) or []:
                    kw = item.get("keyword", "")
                    intent_data = item.get("keyword_intent", {}) or {}
                    intent = intent_data.get("label", "informational")
                    if kw:
                        intent_map[kw] = intent
    except Exception:
        pass
    return intent_map


def _cluster_keywords(keywords: List[Dict], intent_map: Dict[str, str]) -> Dict[str, List[Dict]]:
    """Group keywords into topic clusters by shared words."""
    clusters = defaultdict(list)
    stop_words = {"how", "to", "best", "for", "the", "a", "an", "and", "or", "in", "on", "what", "is"}

    for kw_data in keywords:
        kw = kw_data["keyword"]
        intent = intent_map.get(kw, "informational")
        kw_data["intent"] = intent

        # Extract most meaningful word as cluster key
        words = [w.lower() for w in kw.split() if w.lower() not in stop_words and len(w) > 3]
        cluster_key = words[0] if words else "general"
        clusters[cluster_key].append(kw_data)

    return dict(clusters)


def _build_calendar(clusters: Dict[str, List[Dict]], days: int, start_date: datetime) -> List[Dict]:
    """Build calendar entries from clusters, spreading across days."""
    # Determine cadence (posts per week from cluster size)
    all_posts = []
    for cluster, kws in clusters.items():
        if not kws:
            continue
        # First keyword = pillar (if high volume) or standard post
        for i, kw_data in enumerate(kws[:max(1, days // len(clusters))]):
            content_type = _assign_content_type(kw_data, i == 0)
            slug = kw_data["keyword"].lower().replace(" ", "-").replace("'", "")[:60]
            title = _generate_title(kw_data["keyword"], content_type, kw_data.get("intent", "informational"))
            all_posts.append({
                "cluster": cluster,
                "type": content_type,
                "keyword": kw_data["keyword"],
                "title": title,
                "slug": slug,
                "volume": kw_data.get("volume", 0),
                "kd": kw_data.get("kd", 50),
                "cpc": kw_data.get("cpc", 0),
                "intent": kw_data.get("intent", "informational"),
                "calendar_score": kw_data.get("calendar_score", 0)
            })

    # Sort by score (pillar > spoke by calendar_score)
    all_posts.sort(key=lambda x: (x["type"] == "pillar", x.get("calendar_score", 0)), reverse=True)

    # Assign dates - spread posts evenly, exclude weekends for realism
    calendar = []
    date = start_date
    post_idx = 0
    posts_to_schedule = min(len(all_posts), days)  # Up to 1 post/day

    while post_idx < posts_to_schedule:
        if date.weekday() < 5:  # Monday–Friday only
            post = all_posts[post_idx].copy()
            post["date"] = date.strftime("%Y-%m-%d")
            post["day"] = date.strftime("%A")
            calendar.append(post)
            post_idx += 1
        date += timedelta(days=1)
        if (date - start_date).days > days * 2:  # Safety break
            break

    return calendar


def _assign_content_type(kw_data: Dict, is_first_in_cluster: bool) -> str:
    """Assign pillar, hub, or spoke based on volume/kd."""
    volume = kw_data.get("volume", 0)
    kd = kw_data.get("kd", 50)
    intent = kw_data.get("intent", "informational")

    if volume >= PILLAR_VOLUME and intent == "informational":
        return "pillar"
    elif is_first_in_cluster and volume >= 500:
        return "hub"
    else:
        return "spoke"


def _generate_title(keyword: str, content_type: str, intent: str) -> str:
    """Generate an SEO title from keyword + content type."""
    kw = keyword.title()
    if content_type == "pillar":
        return f"The Complete Guide to {kw}"
    elif content_type == "hub":
        return f"{kw}: Everything You Need to Know"
    elif intent == "transactional":
        return f"Best {kw} — Top Picks & Reviews"
    elif "how" in keyword.lower():
        return kw  # Already question-form
    elif "best" in keyword.lower():
        return f"{kw}: Our Top Recommendations"
    else:
        return f"{kw}: A Complete Overview"


def _save_calendar_csv(calendar: List[Dict], path: Path):
    """Save calendar to CSV."""
    if not calendar:
        return
    fieldnames = ["date", "day", "type", "cluster", "title", "keyword", "volume", "kd", "cpc", "intent", "slug"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(calendar)


def _generate_calendar_summary(domain: str, calendar: List[Dict], days: int) -> str:
    """Generate markdown calendar summary."""
    pillars = [p for p in calendar if p["type"] == "pillar"]
    hubs = [p for p in calendar if p["type"] == "hub"]
    spokes = [p for p in calendar if p["type"] == "spoke"]

    lines = [
        f"# Content Calendar: {domain}",
        f"",
        f"**{days}-Day Plan** | {len(calendar)} posts | {len(pillars)} pillar · {len(hubs)} hub · {len(spokes)} spoke",
        f"",
        f"## Full Calendar",
        f"",
        f"| Date | Day | Type | Keyword | Volume | KD | Title |",
        f"|------|-----|------|---------|--------|----|-------|",
    ]

    for post in calendar:
        lines.append(
            f"| {post['date']} | {post['day'][:3]} | **{post['type']}** | "
            f"{post['keyword']} | {post['volume']:,} | {post['kd']} | "
            f"{post['title'][:50]}... |"
        )

    lines.extend([
        f"",
        f"## Publishing Strategy",
        f"",
        f"- **Pillar posts** ({len(pillars)}): Long-form (2,000+ words), target high-volume informational queries",
        f"- **Hub posts** ({len(hubs)}): Medium-form (1,000-1,500 words), link to spokes",
        f"- **Spoke posts** ({len(spokes)}): Focused (700-1,000 words), target long-tail and transactional",
        f"",
        f"## Quick Wins (KD < 30)",
        f"",
    ])
    quick_wins = sorted([p for p in calendar if p["kd"] < 30], key=lambda x: x.get("volume", 0), reverse=True)[:5]
    for post in quick_wins:
        lines.append(f"- **{post['keyword']}** | {post['volume']:,} vol | KD {post['kd']} | {post['date']}")

    return "\n".join(lines)


if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    topics = sys.argv[2:] if len(sys.argv) > 2 else None
    result = content_calendar_builder(domain, seed_topics=topics)
    if not result.get("dry_run"):
        print(result["summary"])
