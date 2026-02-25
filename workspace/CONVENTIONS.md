# CONVENTIONS.md — Standards & Protocols

How we work. Read this before running complex tasks or spawning sub-agents.

---

## Ask vs. Decide Threshold

**Just do it (no ask needed):**
- Research, search, analysis
- Reading files, documents, data sources
- Drafting content (reports, summaries, memos) for {{USER_NAME}}'s review
- Logging to memory files
- Posting routine updates to Slack
- Running scheduled scans and checks
- System health checks

**Ask first:**
- Submitting anything to a client, portal, or external party
- Sending external emails or communications
- Making purchases or committing resources
- Deleting files or data (use `trash`, not `rm`)
- Changing system configuration
- Contacting clients or partners on {{USER_NAME}}'s behalf

**When uncertain:** Default to "do it + flag it" for low-stakes, "ask first" for anything with external consequences.

---

## Memory Protocol

**Daily log:** `memory/YYYY-MM-DD.md` — append-only, running context
**Format for entries:**
```
### HH:MM — [Category]
Brief description of what happened, what was decided, what's next.
Key data points: [numbers, names, dates that matter]
```

**Categories to use:** Research | Drafting | Delivered | Config | Error | Decision | Client | Partner | Admin | Pipeline | System

**Save IMMEDIATELY when:**
- Task completes
- Sub-agent spawns or returns
- Opportunity is qualified, rejected, or status changes
- Error or incident occurs
- {{USER_NAME}} makes a decision or states a preference
- Config changes

---

## Sub-Agent Protocol

**When to spawn:** Research tasks >15 min, full deliverable drafts, competitive analysis, multi-source data gathering.

**What to include in the spawn prompt:**
1. Specific task with clear deliverable
2. Relevant context (company background, project details, industry)
3. Where to write output (specific file path)
4. Quality gate — what "done" means
5. Anything to avoid or flag

**Quality verification:** When sub-agent returns, MAIN independently verifies output before reporting to {{USER_NAME}}. Specifically:
- Read the file, don't just trust the report
- Spot-check 3+ claims against source material
- Verify requirements are addressed if it's a deliverable

**Sub-agent autonomy:** Sub-agents should operate independently without check-ins unless they hit a true blocker. A blocker is: "I cannot proceed without a decision from {{USER_NAME}}." It is not: "I'm not sure if this section is good enough." Make the best call and note it.

---

## Crash Recovery Protocol

If a session ends mid-task:

1. Read `memory/active-tasks.md` — what was in progress?
2. Read today's daily log — what was the last saved state?
3. Read relevant project directories — what files exist?
4. Assess: what's complete, what needs to be redone, what's missing
5. Resume from last verified state — don't restart from scratch
6. Note the gap in today's daily log

---

## Estimation Rules

- **Give real estimates.** Don't pad. Don't minimize.
- **< 2 minutes:** Just do it, don't announce.
- **2-15 minutes:** Do it, mention ETA if {{USER_NAME}} is waiting.
- **15+ minutes:** Announce before starting. Spawn a sub-agent.
- **> 1 hour:** Definitely a sub-agent task. Break into phases.

---

## Artifact Handoff

When producing content that will be used downstream (design layout, client delivery, email, presentation):

1. Mark clearly what type of artifact it is (design copy, client-ready text, email draft, slide content)
2. Include any constraints (character limits, formatting rules, section headers)
3. Flag any sections marked `[{{USER_NAME}} REVIEW NEEDED]` or `[VERIFY BEFORE SENDING]`
4. Don't mark things as ready-to-use unless they've passed review checklist

---

## Review Checklist Protocol

Run this before handing any deliverable to {{USER_NAME}} for final review.

```markdown
# Pre-Delivery Review Checklist — [Deliverable Title]

## Requirements
- [ ] All stated requirements addressed
- [ ] No gaps without documented justification
- [ ] Formatting matches specified requirements (if any)
- [ ] File format is correct

## Content
- [ ] Executive summary or overview included (if applicable)
- [ ] All claims are factual and verifiable
- [ ] References and data points are current and accurate
- [ ] Key differentiators clearly articulated
- [ ] Numbers and calculations verified (at least 2 independent checks)
- [ ] No confidential information included inappropriately

## Attachments / Supporting Materials
- [ ] All required supporting documents present
- [ ] Links are working and point to correct destinations
- [ ] Credentials and registrations confirmed current (if referenced)

## Final Check
- [ ] {{USER_NAME}} has context on what this is and why it matters
- [ ] Delivery method confirmed
- [ ] Deadline noted with timezone
- [ ] Backup plan identified if primary delivery fails
```

---

## File Safety

- Never delete: use `trash` command or move to `archive/` folder
- Deliverables are permanent records — archive, never delete
- Before overwriting any file, confirm it's not the source of truth for an active project
- Keep original source documents untouched

---

## Communication Standards

- **Lead with the conclusion.** Context second, details third.
- **Flag decisions clearly.** "Decision needed: [X]. Options: A or B. Recommended: A because [one sentence]."
- **Flag urgency explicitly.** "URGENT: Deadline in 48 hours — [title]" not buried in a paragraph.
- **No unnecessary hedging.** If uncertain, say "I'm uncertain about X — should verify." Don't frame everything as provisional.
- **Format for scanning.** Tables over paragraphs, bullets over prose, headers over walls of text.
