# Activity Logging Protocol

## When to Log
- Task started / completed / failed
- Opportunities identified / scored / pursued
- Competitor intelligence gathered
- Client deliverables sent
- System health checks
- Cron job results

## Where to Log
- **Daily memory:** `memory/YYYY-MM-DD.md` — append-only running context
- **Pipeline:** `memory/pipeline.md` — opportunity and deal tracking
- **Incidents:** `memory/incidents.md` — when things break
- **Active tasks:** `memory/active-tasks.md` — current work items

## Format
```markdown
### HH:MM — [Category]
Brief description + key details.
```

## Categories
- `Opportunity Scan` — new leads or opportunities found
- `Pipeline Update` — deal or project status changes
- `Competitor Intel` — competitive intelligence gathered
- `Client Delivery` — deliverable sent to client
- `Research` — market research, analysis completed
- `System Health` — health check results
- `Task` — general task completion
- `Cron` — scheduled job results
- `Decision` — {{USER_NAME}} approved/rejected something
- `Knowledge Update` — new information added to knowledge base
