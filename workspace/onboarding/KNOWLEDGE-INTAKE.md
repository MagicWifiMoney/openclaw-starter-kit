# KNOWLEDGE-INTAKE.md — Building {{AGENT_NAME}}'s Brain

**This is NOT a document {{USER_NAME}} reads. This is YOUR guide for systematically extracting company knowledge through natural conversation. Ask for things when they're relevant, not all at once.**

---

## The Approach

Don't hand {{USER_NAME}} a checklist. Instead, weave knowledge requests into natural moments:

- Working on a proposal or deliverable? → "Do you have a past example for something similar I can reference?"
- Discussing a client? → "Want me to add them to the contacts database with the details you just shared?"
- Talking about competitors? → "Who else would be in the running for something like this? I'll start a competitor file."
- Reviewing pricing? → "Can I save this to your pricing knowledge base so I have it for future quotes?"

---

## Knowledge Categories (Track Progress)

### 1. Company Foundation
**What you need:**
- Current company overview, pitch deck, or one-pager (ANY format — PDF, doc, web page, even verbal)
- How {{USER_NAME}} describes {{COMPANY}} in 30 seconds (the elevator pitch)
- Business registrations, licenses, and certifications relevant to your industry
- Legal entity info, founding date, headquarters location
- Any relevant accreditations, awards, or compliance certifications

**How to ask:**
> "I want to make sure I'm positioning {{COMPANY}} correctly in everything I write. Can you share your company overview or pitch deck? Even just telling me how you describe the business works."

### 2. Past Work / Case Studies (HIGHEST VALUE)
**What you need:**
- 2-3 completed deliverables (wins AND losses if applicable)
- For each: who was the client, what was the brief, what did you deliver, what was the result
- Any client feedback or testimonials
- Metrics and outcomes: "increased revenue 40%", "reduced processing time by 3x", etc.

**How to ask:**
> "The fastest way for me to learn your style and how you position {{COMPANY}} is to read an actual deliverable. Can you share a recent one? Doesn't matter if it went perfectly — I learn from everything."

**Why this matters:** Past deliverables contain writing style, structure, positioning, and quality standards — it's 10x more valuable than any template.

### 3. Team & Key Personnel
**What you need:**
- {{USER_NAME}}'s full bio (education, background, publications, certifications)
- Co-founder / partner bios
- Key team members and their specializations
- Org chart (even informal — who reports to whom)
- Any certifications, licenses, or credentials held by team

**How to ask:**
> "Most client-facing work needs a team section or bio. Can you give me bios for the core team? Even LinkedIn profiles work — I'll format them properly."

### 4. Portfolio / Past Performance
**What you need:**
- Completed projects or engagements with: client, scope, value, timeline, deliverables, outcomes
- Client references (name, title, email, phone — with permission to use)
- Quantifiable metrics: "served 500+ customers", "managed $2M budget", "delivered in 6 weeks", etc.
- Testimonials, recommendations, or case study write-ups

**How to ask:**
> "Your website mentions [specific claim or project]. Can you give me the full story on that engagement? I'll write it up as a reusable case study."

### 5. Products & Technical Specs
**What you need:**
- Product/service descriptions with features, benefits, and technical details
- Pricing tiers or service packages
- Technical documentation, spec sheets, or feature lists
- Architecture overview or integration capabilities (if technical product)
- Any whitepapers, presentations, or publications
- Patent or IP information if applicable

**How to ask:**
> "When I'm writing about {{COMPANY}}'s offerings, I need to be specific about your capabilities. Can you share product docs, feature lists, or spec sheets? The more detail, the better I can position your differentiators."

### 6. Competitive Intelligence
**What you need:**
- Top 5 competitors by name
- What they offer vs what {{COMPANY}} offers
- Where they win (and why)
- Where {{COMPANY}} wins (and why)
- Pricing intelligence if known

**How to ask:**
Build this organically from conversations. When {{USER_NAME}} mentions a competitor or a lost deal:
> "Who won that one? I'll add them to the competitor file. Anything you know about why they got it?"

### 7. Pricing & Business
**What you need:**
- Service/product pricing structure (hourly rates, project fees, retainers, subscriptions)
- Typical deal sizes and contract lengths
- Margin targets or pricing guardrails
- Discount policies or negotiation ranges
- Revenue model and key revenue streams

**How to ask (SENSITIVE — be respectful):**
> "For quotes and proposals, I need to understand your pricing model. This stays in your private knowledge base — no one else sees it. Can you share your rate card or typical pricing structure?"

### 8. Reusable Content / Boilerplate
**What you need:**
- Company description (standard paragraph used in proposals/pitches)
- Service/product descriptions (pre-written)
- Quality or methodology approach
- Security/compliance approach (if applicable)
- Team or organizational structure description
- Any "standard paragraphs" reused across multiple documents

**How to ask:**
> "Do you have any 'standard paragraphs' you reuse across proposals, pitches, or client documents? Things like company overview, methodology, team description? I'll store them as boilerplate so I can drop them into drafts automatically."

### 9. Relationships & Network
**What you need:**
- Key client contacts and relationship status
- Partners, vendors, and subcontractors you work with
- Industry contacts and referral sources
- Professional associations or communities
- Advisory board or mentors

**How to ask (build over time):**
> "You mentioned working with [person/company]. Want me to add them to the contacts database? Knowing your network helps me spot opportunities where you have an inside track."

---

## Storage Protocol

When {{USER_NAME}} shares any document or information:

1. **Acknowledge it:** "Got it — saving to knowledge base."
2. **Categorize it:** Put in the right `knowledge/` subfolder
3. **Extract key facts:** Pull out reusable data points (metrics, dates, names, certifications)
4. **Update MEMORY.md:** Add durable facts to long-term memory
5. **Update relevant files:** If it affects deliverables, update boilerplate. If it affects team, update USER.md.

### File Organization
```
knowledge/
├── company/           # Overview, registrations, certs, org chart
├── deliverables/      # Past work product organized by client/project
│   ├── wins/
│   └── losses/
├── case-studies/      # Reusable project summaries with metrics
├── team/              # Bios, resumes, certifications, specializations
├── products/          # Specs, datasheets, feature lists
├── competitors/       # One file per competitor with intel
├── boilerplate/       # Reusable content sections
├── pricing/           # Rate cards, pricing models (SENSITIVE)
├── contacts/          # Client contacts, partners, references
└── templates/         # Response templates, checklists, frameworks
```

---

## Progress Tracking

Keep this updated in `memory/active-tasks.md`:

```
## Knowledge Base Status
Foundation:   [ ] company overview  [ ] registrations  [ ] certifications
Deliverables: [ ] first example uploaded  [ ] win example  [ ] loss example
Team:         [ ] {{USER_NAME}} bio  [ ] co-founder bio  [ ] key personnel
Products:     [ ] product specs  [ ] pricing  [ ] feature list
Competitors:  [ ] top 3 identified  [ ] comparison matrix started
Pricing:      [ ] rate card  [ ] typical deal sizes
Boilerplate:  [ ] company overview  [ ] methodology  [ ] team description
```

## Proactive Nudges

During heartbeats, if knowledge gaps exist, gently prompt:

> "Quick one — I still don't have team bios for key personnel. That's the #1 thing that slows down proposal and pitch drafts. Want to knock those out today?"

Keep nudges to max 1 per day. Don't nag.
