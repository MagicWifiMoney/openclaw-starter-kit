---
name: schematron
description: Extract structured JSON from messy HTML/web pages using Schematron (inference.net). 770x cheaper than GPT-4 for web scraping. Use when parsing SAM.gov opportunity pages, competitor websites, RFP documents, government HTML, or any web page into clean structured data.
---

# Schematron — HTML → JSON Extraction

Extract structured data from any web page at near-zero cost. Uses inference.net's Schematron-3B/8B models — purpose-built for HTML → JSON extraction.

## Why Use This

| Method | Cost per Page | Speed |
|--------|--------------|-------|
| GPT-4 / Claude | $0.05-0.50 | Slow |
| Schematron-3B | $0.00013 | Fast |
| **Savings** | **770x cheaper** | |

Schematron-8B scores 4.64/5 on extraction benchmarks (GPT-4 scores 4.74 — only 2% better at 50x the cost).

## Setup

```bash
# API Key (OpenAI-compatible endpoint)
export INFERENCE_API_KEY="YOUR_INFERENCE_NET_API_KEY"
```

### Getting Your API Key
1. Go to https://inference.net and create an account
2. Navigate to **API Keys** in your dashboard
3. Generate a new key — it will start with `inference-`
4. Add it to your `.env` file as `INFERENCE_API_KEY`
5. Pricing: ~$0.02/1M input tokens, $0.05/1M output tokens (very cheap)

The API is OpenAI-compatible — use the OpenAI SDK with a custom base URL.

## Quick Example

```python
#!/usr/bin/env python3
"""Extract structured data from any HTML page using Schematron"""

import os, json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("INFERENCE_API_KEY"),
    base_url="https://api.inference.net/v1"
)

def extract(html: str, schema: dict, prompt: str = "Extract the data from this HTML.") -> dict:
    """Extract structured JSON from HTML using Schematron-3B"""
    response = client.chat.completions.create(
        model="inference-net/schematron-3b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": html}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "extraction",
                "strict": True,
                "schema": schema
            }
        },
        temperature=0
    )
    return json.loads(response.choices[0].message.content)
```

## Government Use Cases

### 1. SAM.gov Opportunity Detail Extraction

Parse full SAM.gov opportunity pages into structured data for pipeline tracking.

```python
# Schema for SAM.gov opportunity detail page
SAM_OPPORTUNITY_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Opportunity title"},
        "solicitation_number": {"type": "string"},
        "agency": {"type": "string", "description": "Awarding agency"},
        "sub_agency": {"type": "string"},
        "posted_date": {"type": "string"},
        "response_deadline": {"type": "string"},
        "set_aside": {"type": "string", "description": "Small business set-aside type if any"},
        "naics_code": {"type": "string"},
        "naics_description": {"type": "string"},
        "classification_code": {"type": "string"},
        "place_of_performance": {"type": "string"},
        "description_summary": {"type": "string", "description": "First 500 chars of the description"},
        "contact_name": {"type": "string"},
        "contact_email": {"type": "string"},
        "contact_phone": {"type": "string"},
        "estimated_value": {"type": "string", "description": "Estimated contract value if listed"},
        "attachments_count": {"type": "integer", "description": "Number of attached documents"},
        "award_type": {"type": "string", "description": "Contract, grant, cooperative agreement, etc."}
    },
    "required": ["title", "solicitation_number", "agency", "response_deadline", "naics_code", "description_summary"],
    "additionalProperties": false
}

# Usage with web_fetch:
# 1. Fetch the SAM.gov opportunity page HTML
# 2. Pass to Schematron for extraction
# 3. Score against Go/No-Go matrix
# 4. Add to rfp-pipeline.md if score >= 15
```

### 2. Competitor Website Intelligence

Scrape competitor websites for capabilities, past performance, and team info.

```python
COMPETITOR_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "tagline": {"type": "string"},
        "headquarters": {"type": "string"},
        "employee_count": {"type": "string"},
        "year_founded": {"type": "string"},
        "capabilities": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of stated capabilities/services"
        },
        "industries_served": {
            "type": "array",
            "items": {"type": "string"}
        },
        "certifications": {
            "type": "array",
            "items": {"type": "string"},
            "description": "8(a), HUBZone, SDVOSB, ISO, CMMI, etc."
        },
        "notable_clients": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Government agencies or major clients mentioned"
        },
        "contract_vehicles": {
            "type": "array",
            "items": {"type": "string"},
            "description": "GSA Schedule, SEWP, CIO-SP3, etc."
        },
        "key_personnel": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "title": {"type": "string"},
                    "background": {"type": "string"}
                },
                "required": ["name", "title"],
                "additionalProperties": false
            }
        },
        "differentiators": {
            "type": "array",
            "items": {"type": "string"},
            "description": "What they claim makes them unique"
        }
    },
    "required": ["company_name", "capabilities"],
    "additionalProperties": false
}
```

### 3. RFP Document Parsing

Extract key requirements from RFP HTML/text (for documents converted from PDF).

```python
RFP_REQUIREMENTS_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "issuing_agency": {"type": "string"},
        "solicitation_number": {"type": "string"},
        "response_deadline": {"type": "string"},
        "period_of_performance": {"type": "string"},
        "contract_type": {"type": "string", "description": "FFP, T&M, Cost-Plus, IDIQ, etc."},
        "estimated_value": {"type": "string"},
        "set_aside": {"type": "string"},
        "technical_requirements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key technical requirements extracted from SOW/PWS"
        },
        "evaluation_criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "factor": {"type": "string"},
                    "weight": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["factor"],
                "additionalProperties": false
            }
        },
        "deliverables": {
            "type": "array",
            "items": {"type": "string"}
        },
        "required_certifications": {
            "type": "array",
            "items": {"type": "string"}
        },
        "security_clearance": {"type": "string", "description": "Clearance level required if any"},
        "page_limit": {"type": "string", "description": "Page limit for technical volume"},
        "submission_format": {"type": "string", "description": "Email, SAM.gov, grants.gov, etc."},
        "questions_deadline": {"type": "string"},
        "incumbent": {"type": "string", "description": "Current contractor if mentioned"}
    },
    "required": ["title", "issuing_agency", "response_deadline", "technical_requirements"],
    "additionalProperties": false
}
```

### 4. Government News/Press Release Extraction

Monitor agency press releases for contract awards, new initiatives, budget announcements.

```python
GOV_NEWS_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {"type": "string"},
        "date": {"type": "string"},
        "agency": {"type": "string"},
        "summary": {"type": "string", "description": "2-3 sentence summary"},
        "contract_awards_mentioned": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string"},
                    "amount": {"type": "string"},
                    "purpose": {"type": "string"}
                },
                "required": ["recipient"],
                "additionalProperties": false
            }
        },
        "relevance_to_company": {"type": "string", "description": "Why this matters for your company's pipeline"},
        "action_items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Suggested follow-up actions"
        }
    },
    "required": ["headline", "date", "summary"],
    "additionalProperties": false
}
```

## Workflow: Batch Scraping Pipeline

```python
#!/usr/bin/env python3
"""Batch scrape and extract — e.g., process 100 SAM.gov opportunities"""

import os, json, time, requests
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("INFERENCE_API_KEY"),
    base_url="https://api.inference.net/v1"
)

def clean_html(raw_html: str) -> str:
    """Strip scripts, styles, nav — keep content"""
    from lxml.html.clean import Cleaner
    import lxml.html as LH
    cleaner = Cleaner(scripts=True, javascript=True, style=True, 
                      inline_style=True, safe_attrs_only=False)
    doc = LH.fromstring(raw_html)
    cleaned = cleaner.clean_html(doc)
    return LH.tostring(cleaned, encoding="unicode")

def extract_page(url: str, schema: dict, prompt: str) -> dict:
    """Fetch URL → clean HTML → extract JSON"""
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    html = clean_html(resp.text)
    
    # Truncate to 100K chars if needed (128K token context)
    if len(html) > 100000:
        html = html[:100000]
    
    result = client.chat.completions.create(
        model="inference-net/schematron-3b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": html}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "extraction", "strict": True, "schema": schema}
        },
        temperature=0
    )
    return json.loads(result.choices[0].message.content)

# Example: batch process SAM.gov opportunities
urls = [
    "https://sam.gov/opp/abc123/view",
    "https://sam.gov/opp/def456/view",
    # ... 
]

results = []
for url in urls:
    try:
        data = extract_page(url, SAM_OPPORTUNITY_SCHEMA, "Extract all opportunity details from this SAM.gov page.")
        results.append(data)
        time.sleep(0.5)  # Be respectful
    except Exception as e:
        print(f"Failed: {url} — {e}")

# Save results
with open("opportunities.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Extracted {len(results)} opportunities")
# Cost: 100 pages × ~5K tokens × $0.02/1M = $0.01 total
```

## Models Available

| Model | Quality (1-5) | Cost (input/output per 1M) | Best For |
|-------|--------------|---------------------------|----------|
| `inference-net/schematron-3b` | 4.41 | $0.02 / $0.05 | High volume, simple schemas |
| `inference-net/schematron-8b` | 4.64 | $0.05 / $0.10 | Complex schemas, higher accuracy |

**Default to schematron-3b** — it handles 95% of use cases. Use 8b only for complex nested schemas or when 3b misses fields.

## Tips

1. **Clean HTML first** — strip scripts, styles, navigation. Schematron works on content, not chrome.
2. **Schema must be strict** — `"strict": True` and `"additionalProperties": false` on all objects.
3. **All fields in `required`** — use nullable types (`"type": ["string", "null"]`) for optional fields rather than omitting from required.
4. **128K context** — can handle huge government pages, but cleaning first saves tokens and improves accuracy.
5. **Batch overnight** — schedule heavy scraping in the agent's overnight health window (2am local) to avoid rate limits.
