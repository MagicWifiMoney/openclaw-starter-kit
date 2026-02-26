## Learnings

### Hard Rules
- **NEVER guess or fabricate data.** If you can't verify something, either look it up properly or leave it blank/"Unknown". Guessing and presenting it as fact is a trust-breaker.
- **QA EVERYTHING before it goes live.** Content, dashboards, links, deliverables — nothing ships without verification. Sub-agents verify their own work, then main session independently verifies before reporting done. Cross-check 3+ data points. If you can't confirm accuracy, flag for review — don't push it.

### What Works Well
- **Overnight autonomous work (1am-5am):** Processing queued tasks while the user sleeps — high value, zero interruption
- **Morning briefing + weekly audit:** Proactive reporting with clear recommendations
- **Staggered cron scheduling:** Never run multiple crons at the exact same minute
- **Surprise deliverables:** Building things based on interview answers without being asked — dashboards, competitive briefs, organized knowledge bases

### Cron Scheduling (CRITICAL)
**NEVER schedule multiple crons at the exact same minute.** Each isolated cron spawns a Claude session. Parallel spawns overwhelm the gateway → timeouts → nothing runs.

**Rules:**
1. Before adding a new cron, check existing times
2. Stagger by at least 5 minutes from any existing cron
3. Prefer odd minutes (:05, :15, :25, :35, :45, :55) to avoid collisions
4. Morning crons (6-9am) are highest risk — extra spacing needed

### Tool Gotchas
- HTML cleaning before Schematron extraction saves tokens and improves accuracy
- Rate limits: be respectful with all external APIs (1-2 second delays between requests)
- API keys expire — track expiration dates in MEMORY.md
- Always test API responses with a small request before running bulk operations
- PDF parsing: check output quality before processing entire documents

### Government API Notes
*(Only relevant if using the gov contracting industry module)*
- **SAM.gov API** requires date range (max 1 year between postedFrom and postedTo)
- **Grants.gov** API response structure nests data under `data.oppHits`
- **Schematron** (inference.net) needs `"strict": true` and `"additionalProperties": false` in all JSON schemas
