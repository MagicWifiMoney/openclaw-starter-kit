---
name: arxiv
description: Search and browse academic papers on arXiv
version: 1.0.0
author: botti
enabled: true
tools:
  - name: arxiv_search
    description: "Search arXiv papers by keyword, get paper details, and browse abstracts"
    command: "python3 scripts/arxiv_search.py"
    args:
      - name: action
        description: "Action: search, details"
        required: true
      - name: query
        description: "Search query or arXiv paper ID"
        required: true
      - name: --max-results
        description: "Max results to return (default 10)"
        required: false
      - name: --sort
        description: "Sort order: relevance, submitted, updated"
        required: false
      - name: --category
        description: "Filter by arXiv category (e.g. cs.AI, cs.LG, cs.CL)"
        required: false
---

# arXiv Papers

Search and browse academic papers on [arXiv.org](https://arxiv.org).

## Usage

### Search papers
```bash
python3 scripts/arxiv_search.py search "large language models" --max-results 5 --sort relevance
```

### Search with category filter
```bash
python3 scripts/arxiv_search.py search "reinforcement learning" --category cs.LG --max-results 10
```

### Get paper details
```bash
python3 scripts/arxiv_search.py details "2401.12345"
```

### Supported categories
`cs.AI`, `cs.LG`, `cs.CL`, `cs.CV`, `cs.RO`, `stat.ML`, `math.OC`, etc.

### Sort options
- `relevance` (default)
- `submitted` (newest first)
- `updated` (recently updated first)
