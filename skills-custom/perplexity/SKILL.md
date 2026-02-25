---
name: perplexity
description: Research queries with citations using the Perplexity API (sonar models)
version: 1.0.0
author: botti
tags: [research, search, citations, ai]
enabled: true
---

# Perplexity API Skill

Research the web with AI-powered answers and citations via the Perplexity API.

## Usage

```bash
python3 scripts/perplexity_search.py "What are the latest advances in fusion energy?"
python3 scripts/perplexity_search.py "Compare React vs Vue in 2025" --model sonar-pro
python3 scripts/perplexity_search.py "Best practices for RAG pipelines" --citations
```

## Models

| Model | Description |
|-------|-------------|
| `sonar` | Fast, default — good for quick lookups |
| `sonar-pro` | Deeper research — better for complex questions |

## Options

- `--model sonar|sonar-pro` — Model to use (default: sonar)
- `--citations` — Explicitly request citation URLs in output
- `--follow-up "question"` — Ask a follow-up (includes prior context)

## Environment

Requires `PERPLEXITY_API_KEY` in environment or `~/clawd/.env`.

## Output

Clean markdown with the answer and numbered citation URLs.
