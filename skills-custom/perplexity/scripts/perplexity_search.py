#!/usr/bin/env python3
"""Perplexity API search with citations."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_URL = "https://api.perplexity.ai/chat/completions"


def get_api_key():
    key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not key:
        # Try loading from .env
        env_path = os.path.expanduser("~/clawd/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("PERPLEXITY_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip("'\"")
                        break
    if not key:
        print("Error: PERPLEXITY_API_KEY not found in environment or ~/clawd/.env", file=sys.stderr)
        sys.exit(1)
    return key


def query(question, model="sonar", history=None):
    api_key = get_api_key()
    messages = history or []
    messages.append({"role": "user", "content": question})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "return_citations": True,
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

    content = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])

    return content, citations, messages + [{"role": "assistant", "content": content}]


def format_output(content, citations, show_citations=True):
    out = content + "\n"
    if show_citations and citations:
        out += "\n---\n**Sources:**\n"
        for i, url in enumerate(citations, 1):
            out += f"{i}. {url}\n"
    return out


def main():
    parser = argparse.ArgumentParser(description="Search with Perplexity API")
    parser.add_argument("question", help="Research question")
    parser.add_argument("--model", choices=["sonar", "sonar-pro"], default="sonar", help="Model (default: sonar)")
    parser.add_argument("--citations", action="store_true", default=True, help="Show citation URLs (default: on)")
    parser.add_argument("--follow-up", dest="followup", help="Follow-up question (uses prior context)")
    args = parser.parse_args()

    content, citations, history = query(args.question, model=args.model)
    print(format_output(content, citations, args.citations))

    if args.followup:
        print("\n--- Follow-up ---\n")
        content2, citations2, _ = query(args.followup, model=args.model, history=history)
        print(format_output(content2, citations2, args.citations))


if __name__ == "__main__":
    main()
