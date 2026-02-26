#!/usr/bin/env python3
"""
Quick test - verifies enrichment is working with known IPs.
Run: python3 test_enrich.py
"""

import json
import sys
sys.path.insert(0, '.')
from enrich import enrich

TEST_IPS = [
    ("8.8.8.8",     "Google"),          # Google DNS - should come back as Google
    ("208.67.222.222", "OpenDNS"),       # Cisco OpenDNS
    ("205.1.255.1",    "Boeing"),        # Boeing corporate range
    ("192.168.1.1",    "Private"),       # Private - should skip
]

print("Testing IP enrichment (no API key needed)...\n")
all_passed = True

for ip, expected_keyword in TEST_IPS:
    result = enrich(ip)
    org = result.get("org", "")
    passed = expected_keyword.lower() in org.lower() or result.get("source") == "skip"
    status = "PASS" if passed else "FAIL"
    if not passed:
        all_passed = False
    print(f"[{status}] {ip}")
    print(f"       Expected: contains '{expected_keyword}'")
    print(f"       Got:      {org} (source: {result.get('source')})")
    print()

if all_passed:
    print("All tests passed. Enrichment is working.")
    sys.exit(0)
else:
    print("Some tests failed. Check connectivity to ip-api.com")
    sys.exit(1)
