#!/usr/bin/env python3
"""arXiv paper search and details CLI using the free Atom API."""

import argparse
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

BASE = "https://export.arxiv.org/api/query"


def fetch(params, retries=3):
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sL", "-m", "30", url],
                capture_output=True, text=True, timeout=35
            )
            if result.returncode != 0:
                raise RuntimeError(f"curl failed: {result.stderr}")
            if not result.stdout.strip().startswith("<?xml"):
                raise RuntimeError(f"Non-XML response: {result.stdout[:100]}")
            return ET.fromstring(result.stdout)
        except Exception as e:
            if attempt < retries - 1:
                wait = 10 * (attempt + 1)
                print(f"⏳ Retry {attempt+1}/{retries}: waiting {wait}s... ({e})", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"❌ arXiv API error after {retries} attempts: {e}", file=sys.stderr)
            print("   The arXiv API rate-limits to ~1 request per 3 seconds.", file=sys.stderr)
            print("   Wait a minute and try again.", file=sys.stderr)
            sys.exit(1)


def parse_entry(entry):
    title = entry.findtext("atom:title", "", NS).replace("\n", " ").strip()
    abstract = entry.findtext("atom:summary", "", NS).replace("\n", " ").strip()
    published = entry.findtext("atom:published", "", NS)[:10]
    authors = [a.findtext("atom:name", "", NS) for a in entry.findall("atom:author", NS)]
    categories = [c.get("term") for c in entry.findall("atom:category", NS)]
    arxiv_url = ""
    pdf_url = ""
    for link in entry.findall("atom:link", NS):
        if link.get("type") == "text/html":
            arxiv_url = link.get("href", "")
        elif link.get("title") == "pdf":
            pdf_url = link.get("href", "")
    if not arxiv_url:
        arxiv_url = entry.findtext("atom:id", "", NS)
    return {
        "title": title,
        "authors": authors,
        "published": published,
        "abstract": abstract,
        "categories": categories,
        "url": arxiv_url,
        "pdf": pdf_url,
    }


def format_paper(p, full=False):
    authors = ", ".join(p["authors"][:10])
    if len(p["authors"]) > 10:
        authors += f" (+{len(p['authors']) - 10} more)"
    abstract = p["abstract"]
    if not full:
        abstract = abstract[:300] + ("..." if len(abstract) > 300 else "")
    cats = ", ".join(p["categories"])
    return "\n".join([
        f"### {p['title']}",
        f"**Authors:** {authors}",
        f"**Published:** {p['published']}",
        f"**Categories:** {cats}",
        f"**URL:** {p['url']}",
        f"**PDF:** {p['pdf']}",
        "",
        f"> {abstract}",
        "",
        "---",
    ])


def do_search(query, max_results=10, sort="relevance", category=None):
    sort_map = {
        "relevance": "relevance",
        "submitted": "submittedDate",
        "updated": "lastUpdatedDate",
    }
    search_query = f"all:{query}"
    if category:
        search_query = f"cat:{category} AND all:{query}"

    params = {
        "search_query": search_query,
        "max_results": max_results,
        "sortBy": sort_map.get(sort, "relevance"),
        "sortOrder": "descending",
    }
    root = fetch(params)
    entries = root.findall("atom:entry", NS)

    if not entries:
        print("No papers found.")
        return

    print(f"## arXiv Search: \"{query}\" ({len(entries)} results)\n")
    for entry in entries:
        p = parse_entry(entry)
        if p["title"]:  # skip empty/error entries
            print(format_paper(p))
            print()


def do_details(paper_id):
    paper_id = paper_id.strip().replace("https://arxiv.org/abs/", "").replace("http://arxiv.org/abs/", "")
    params = {"id_list": paper_id, "max_results": 1}
    root = fetch(params)
    entries = root.findall("atom:entry", NS)
    if not entries:
        print(f"Paper not found: {paper_id}")
        sys.exit(1)

    p = parse_entry(entries[0])
    if not p["title"]:
        print(f"Paper not found: {paper_id}")
        sys.exit(1)

    print("## Paper Details\n")
    print(format_paper(p, full=True))


def main():
    parser = argparse.ArgumentParser(description="arXiv paper search")
    sub = parser.add_subparsers(dest="action", required=True)

    sp = sub.add_parser("search")
    sp.add_argument("query")
    sp.add_argument("--max-results", type=int, default=10)
    sp.add_argument("--sort", choices=["relevance", "submitted", "updated"], default="relevance")
    sp.add_argument("--category", help="Filter by arXiv category (e.g. cs.AI)")

    dp = sub.add_parser("details")
    dp.add_argument("paper_id")

    args = parser.parse_args()

    if args.action == "search":
        do_search(args.query, args.max_results, args.sort, args.category)
    elif args.action == "details":
        do_details(args.paper_id)


if __name__ == "__main__":
    main()
