#!/usr/bin/env python3
"""
Standalone IP enricher. No API key needed.
Reads IPs from stdin or a file, enriches via ip-api.com + RDAP fallback.

Usage:
  echo "8.8.8.8" | python3 enrich.py
  cat ips.txt | python3 enrich.py
  python3 enrich.py --ip 8.8.8.8
  python3 enrich.py --file ips.txt --output results.json

ip-api.com: HTTP, no key, 1000 req/hour
RDAP: HTTPS, no key, no limit (public internet registry)
"""

import sys
import json
import time
import argparse
import ipaddress
from urllib.request import urlopen
from urllib.error import URLError

# Consumer ISP filter (same as digest.py)
CONSUMER_KEYWORDS = [
    "comcast", "charter", "spectrum", "cox", "at&t", "verizon", "t-mobile",
    "centurylink", "lumen", "frontier", "optimum", "xfinity", "cablevision",
    "mediacom", "windstream", "earthlink", "sprint", "residential",
    "amazon", "aws", "google llc", "microsoft corp", "digitalocean",
    "linode", "vultr", "hetzner", "cloudflare", "fastly", "akamai",
]

def is_private(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False

def enrich_via_ip_api(ip: str) -> dict:
    """ip-api.com - HTTP only, no key, 1000/hr. Best for batch."""
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,org,isp,as,city,country,query"
        with urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        if data.get("status") == "success":
            return {
                "ip": ip,
                "org": data.get("org", ""),
                "isp": data.get("isp", ""),
                "asn": data.get("as", ""),
                "city": data.get("city", ""),
                "country": data.get("country", ""),
                "source": "ip-api.com",
            }
    except Exception:
        pass
    return {}

def enrich_via_rdap(ip: str) -> dict:
    """RDAP - HTTPS, no key, public internet registry. Returns registration data."""
    # Try ARIN first, then RIPE, then APNIC
    registries = [
        f"https://rdap.arin.net/registry/ip/{ip}",
        f"https://rdap.db.ripe.net/ip/{ip}",
        f"https://rdap.apnic.net/ip/{ip}",
    ]
    for url in registries:
        try:
            with urlopen(url, timeout=5) as r:
                data = json.loads(r.read())
            # RDAP structure: entities[0].vcardArray[1] has name
            name = ""
            for entity in data.get("entities", []):
                vcard = entity.get("vcardArray", [None, []])[1]
                for field in vcard:
                    if field[0] == "fn":
                        name = field[3]
                        break
                if name:
                    break
            if not name:
                name = data.get("name", "")
            if name:
                return {
                    "ip": ip,
                    "org": name,
                    "isp": "",
                    "asn": "",
                    "city": "",
                    "country": data.get("country", ""),
                    "source": "rdap",
                }
        except Exception:
            continue
    return {}

def enrich(ip: str) -> dict:
    """Enrich a single IP. Falls back from ip-api.com to RDAP."""
    if is_private(ip):
        return {"ip": ip, "org": "Private/Internal", "source": "skip"}

    result = enrich_via_ip_api(ip)
    if not result.get("org"):
        result = enrich_via_rdap(ip)
    if not result:
        result = {"ip": ip, "org": "Unknown", "source": "none"}

    org_lower = result.get("org", "").lower()
    result["is_consumer"] = any(kw in org_lower for kw in CONSUMER_KEYWORDS)
    return result

def enrich_batch(ips: list, delay: float = 0.2) -> list:
    """Enrich a list of IPs with rate limiting."""
    results = []
    seen = set()
    for ip in ips:
        ip = ip.strip()
        if not ip or ip in seen:
            continue
        seen.add(ip)
        result = enrich(ip)
        results.append(result)
        print(f"  {ip} -> {result.get('org', 'Unknown')} ({result.get('city', '')})",
              file=sys.stderr)
        time.sleep(delay)
    return results

def main():
    parser = argparse.ArgumentParser(description="Enrich IPs with org data")
    parser.add_argument("--ip",     help="Single IP to enrich")
    parser.add_argument("--file",   help="File with one IP per line")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    parser.add_argument("--no-consumers", action="store_true",
                        help="Filter out consumer ISPs from output")
    args = parser.parse_args()

    ips = []
    if args.ip:
        ips = [args.ip]
    elif args.file:
        with open(args.file) as f:
            ips = f.readlines()
    else:
        ips = sys.stdin.readlines()

    print(f"Enriching {len(ips)} IPs...", file=sys.stderr)
    results = enrich_batch(ips)

    if args.no_consumers:
        results = [r for r in results if not r.get("is_consumer")]

    output = json.dumps(results, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)

if __name__ == "__main__":
    main()
