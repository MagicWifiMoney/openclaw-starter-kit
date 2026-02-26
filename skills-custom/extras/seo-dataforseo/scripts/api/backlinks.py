"""Backlinks API - Domain authority, referring domains, and link gap analysis."""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from dataforseo_client.rest import ApiException
from dataforseo_client.api.backlinks_api import BacklinksApi

from core.client import get_client
from core.storage import save_result
from config.settings import settings


def _get_backlinks_api() -> BacklinksApi:
    """Get BacklinksApi instance from the shared api_client."""
    client = get_client()
    return BacklinksApi(client.api_client)


def get_backlinks_summary(
    domain: str,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get domain authority metrics: rank, backlink count, referring domains, spam score.

    Args:
        domain: Target domain (e.g. "competitor.com")
        save: Whether to save results

    Returns:
        Dict with rank, backlinks_num, referring_domains, spam_score, etc.

    Cost: $0.02/domain

    Example:
        >>> result = get_backlinks_summary("competitor.com")
    """
    api = _get_backlinks_api()

    try:
        response = api.summary_live([{
            "target": domain,
            "include_subdomains": True,
            "backlinks_status_type": "live"
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(result, category="backlinks", operation="summary", keyword=domain)

        return result

    except ApiException as e:
        print(f"API Exception (backlinks summary {domain}): {e}")
        raise


def get_bulk_backlinks_summary(
    domains: List[str],
    save: bool = True
) -> Dict[str, Any]:
    """
    Get backlink summaries for multiple domains at once.

    Args:
        domains: List of domains (max 1000)
        save: Whether to save results

    Returns:
        Dict with per-domain rank, backlinks, referring_domains, spam_score

    Cost: $0.02/domain

    Example:
        >>> result = get_bulk_backlinks_summary(["site1.com", "site2.com"])
    """
    api = _get_backlinks_api()

    try:
        response = api.bulk_ranks_live([{
            "targets": domains[:1000]
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(result, category="backlinks", operation="bulk_ranks", keyword=domains[0])

        return result

    except ApiException as e:
        print(f"API Exception (bulk backlinks): {e}")
        raise


def get_referring_domains(
    domain: str,
    limit: int = 100,
    min_rank: int = 10,
    max_spam_score: int = 50,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get referring domains for a target - filtered by quality.

    Args:
        domain: Target domain
        limit: Max results (default 100)
        min_rank: Minimum domain rank (filter out very low DA)
        max_spam_score: Maximum spam score (filter spammy linkers)
        save: Whether to save results

    Returns:
        Dict with referring domain list including rank, backlinks count, etc.

    Cost: ~$0.02/domain

    Example:
        >>> result = get_referring_domains("competitor.com", limit=200)
    """
    api = _get_backlinks_api()

    try:
        response = api.referring_domains_live([{
            "target": domain,
            "limit": min(limit, 1000),
            "order_by": ["rank,desc"],
            "filters": [
                ["rank", ">", min_rank],
                "and",
                ["spam_score", "<", max_spam_score]
            ],
            "backlinks_status_type": "live"
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(result, category="backlinks", operation="referring_domains", keyword=domain)

        return result

    except ApiException as e:
        print(f"API Exception (referring domains {domain}): {e}")
        raise


def get_domain_intersection(
    your_domain: str,
    competitor_domain: str,
    save: bool = True
) -> Dict[str, Any]:
    """
    Find domains linking to competitor but NOT to you (backlink gap).

    Args:
        your_domain: Your domain
        competitor_domain: Competitor domain
        save: Whether to save results

    Returns:
        Dict with domains that link to competitor but not you

    Cost: ~$0.02

    Example:
        >>> result = get_domain_intersection("mysite.com", "competitor.com")
    """
    api = _get_backlinks_api()

    try:
        response = api.domain_intersection_live([{
            "targets": {
                "target1": your_domain,
                "target2": competitor_domain
            },
            "intersections": False,  # False = domains that DON'T intersect (gap)
            "main_target": competitor_domain,
            "limit": 100,
            "order_by": ["rank,desc"],
            "backlinks_status_type": "live"
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(result, category="backlinks", operation="domain_gap",
                       keyword=f"{your_domain}_vs_{competitor_domain}")

        return result

    except ApiException as e:
        print(f"API Exception (domain intersection): {e}")
        raise


def get_domain_pages(
    domain: str,
    limit: int = 50,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get top pages for a domain by backlink count.

    Args:
        domain: Target domain
        limit: Max pages (default 50)
        save: Whether to save results

    Returns:
        Dict with top pages, their backlink counts, and page metrics

    Cost: ~$0.02/domain

    Example:
        >>> result = get_domain_pages("competitor.com", limit=20)
    """
    api = _get_backlinks_api()

    try:
        response = api.domain_pages_live([{
            "target": domain,
            "limit": min(limit, 1000),
            "order_by": ["backlinks,desc"],
            "backlinks_status_type": "live"
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(result, category="backlinks", operation="domain_pages", keyword=domain)

        return result

    except ApiException as e:
        print(f"API Exception (domain pages {domain}): {e}")
        raise
