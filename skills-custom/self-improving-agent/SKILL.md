---
name: self-improving-agent
description: "Captures learnings, verifies work, and logs decisions. Use when: (1) completing a task (verify it worked), (2) making recommendations to Jake (decision format), (3) something goes wrong (incident log), (4) Jake approves/rejects a recommendation (log decision). DON'T use when: quick answers, simple file operations, or casual conversation."
---

# Self-Improving Agent Skill

## Verify → Learn Loop (MANDATORY)

**Never mark work "done" until you VERIFY it actually worked.**

```
1. EXECUTE → Do the work
2. VERIFY → Test/check it actually happened
   - Check live site / run test command / view logs / confirm with API
3. RETRY → If failed, fix and repeat
4. LEARN → Extract lesson before marking done
5. DONE → Only now can you say "complete"
```

### Verification Examples:

**Deploying code (Vercel - MANDATORY):**
- ❌ "Pushed to GitHub, done"
- ✅ "Pushed → Checked Vercel deployment status → Tested live URL → Works ✓"
- After EVERY git push to a Vercel project: run `vercel ls` or check the Vercel dashboard.

**Creating cron:**
- ✅ "Added → Verified in cron list → Next run scheduled → Done ✓"

**Updating files:**
- ✅ "Updated → Read file back → Changes present → Done ✓"

**API changes:**
- ✅ "Updated → Tested with curl → Returns expected data → Done ✓"

### Extract Learnings:
After verification, ask:
- What went wrong?
- What would prevent this next time?
- What's the better approach?

Write to `memory/YYYY-MM-DD.md` immediately.

## Decision Interface Pattern (MANDATORY)

**Every recommendation MUST end with structured decision format:**

```
🎯 ACTION 1: [Specific, actionable title]
📊 Data: [Numbers/facts driving this recommendation]
⚡️ Impact: [Expected outcome with metrics]
💪 Effort: Low/Med/High

🎯 ACTION 2: [Next option]
📊 Data: [Supporting facts]
⚡️ Impact: [What changes]
💪 Effort: Low/Med/High

Reply: "Approve 1" or "Reject 1 - [reason]"
```

**When to use:**
- Project recommendations
- Strategic choices
- Resource allocation
- Process improvements
- Any decision that affects priorities

### Logging Decisions:

When Jake responds with "Approve X" or "Reject X - reason":
1. Log to `memory/decisions/YYYY-MM.md`
2. Track rejection reason (if rejected)
3. Execute approved action
4. Follow up with outcome

**Log format:**
```markdown
## [Date] - [Action Title]
**Decision:** Approved/Rejected
**Reason:** [If rejected]
**Outcome:** [After execution]
**Learning:** [What this teaches]
```

## Proactive Updates (NON-NEGOTIABLE)

**If you say "I'll update you when X is done" - that's a PROMISE.**

1. **Complete the work**
2. **IMMEDIATELY send the update** (don't wait for next message)
3. **Include:** What was done, any issues, next steps

### Completion Summary Template
```
✅ [Task name] complete

What shipped:
- Item 1
- Item 2

Issues (if any):
- Thing that failed + why

Next: [What's next or "all done"]
```

### During Multi-Step Work
- "Step 1/3 done, moving to step 2"
- "Hit a snag with X, trying Y instead"
- "All done - here's what shipped"

## Incident Logging

When something goes wrong:
→ Append to `memory/incidents.md`: `[date] CATEGORY: what happened → fix`

Categories: ROUTING, FILE, AGENT, CONFIG, EXTERNAL, MEMORY
