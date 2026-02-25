# INDUSTRY-PLAYBOOK-GOV.md — Government Contracting Proposal Operations Guide

<!--
  This is an OPTIONAL module for government contracting.
  If you're not in gov contracting, you can safely delete this file.

  To activate: During onboarding Phase 2, if {{USER_NAME}} indicates they pursue
  government contracts, install this playbook and reference it for all RFP pursuits.
-->

This is the operational playbook for every government contract pursuit. Reference it when qualifying a new opportunity, drafting a response, or reviewing before submission.

---

## Go/No-Go Decision Framework

Run this before committing any drafting effort. An hour spent here saves days of wasted work.

### Score the Opportunity (1-3 per criterion)

| Criterion | 1 (Weak) | 2 (Neutral) | 3 (Strong) | Score |
|-----------|----------|-------------|------------|-------|
| **Contract value** | Outside sweet spot (too small or too large for current capacity) | Workable but not ideal | Right in the sweet spot for {{COMPANY}}'s stage | |
| **Capability alignment** | Tangential — would need new capabilities | Partial — core offerings apply with stretch | Direct — aligns with core products/services | |
| **Technical differentiation** | Commodity — many firms can do it | Some — we're competitive | High — unique technology or capabilities are decisive | |
| **Competition level** | Likely wired for incumbent | Open competition, strong field | Likely sole-source or few viable bidders | |
| **Timeline feasibility** | < 3 weeks to proposal due (can't do it right) | 3-6 weeks (tight but doable) | 6+ weeks (enough time to do it well) | |
| **Agency relationship** | Cold — no prior contact | Warm — they know {{COMPANY}} | Hot — prior engagement, invited to respond | |
| **Past performance fit** | No relevant examples | 1-2 similar examples | 3+ directly relevant examples | |
| **Set-aside status** | Full & Open (competing with primes) | Small Business set-aside | SBIR / tech-specific — natural fit | |
| **Strategic value** | One-off, no follow-on | Some — builds past performance | High — opens agency, IDIQ, multi-year potential | |

**Total: __ / 27**

### Verdict

| Score | Decision |
|-------|----------|
| 22-27 | **GO** — Prioritize. Full proposal effort. |
| 16-21 | **GO with caveats** — Pursue but scope the effort to the score. |
| 10-15 | **Borderline** — Discuss with {{USER_NAME}} before committing. |
| < 10 | **NO-GO** — Log the reason, move on. Don't rationalize pursuit. |

### Hard No-Go Triggers (Override Score)

Any one of these = NO-GO regardless of total score:
- [ ] SAM.gov shows a single incumbent with 3+ consecutive awards on this program
- [ ] RFP clearly written to match a competitor's capabilities, not {{COMPANY}}'s
- [ ] Timeline is physically impossible given team capacity
- [ ] Security clearance required that {{COMPANY}} doesn't hold
- [ ] Technology required that doesn't exist in {{COMPANY}}'s stack and can't be partnered
- [ ] {{USER_NAME}} or legal flags a conflict of interest

---

## Pipeline Tracking

**File:** `memory/rfp-pipeline.md`

Every opportunity gets a record, even No-Gos (to avoid re-evaluating the same opportunity later).

```markdown
## [RFP/Grant Title]

| Field | Value |
|-------|-------|
| Solicitation # | [Number] |
| Agency / Office | [e.g., DOE Office of Electricity] |
| Source | [SAM.gov / SBIR / GovWin / other] |
| Type | [Contract / SBIR / Grant / IDIQ] |
| Posted Date | YYYY-MM-DD |
| **Due Date** | **YYYY-MM-DD HH:MM [timezone]** |
| Estimated Value | $[amount] |
| NAICS Code | [code] |
| Set-Aside | [SB / SBIR / Full & Open / other] |
| Go/No-Go Score | [__/27] |
| **Decision** | **GO / NO-GO** |
| Decision Rationale | [One sentence] |
| Lead | [Name] |
| Status | Qualifying / Drafting / Review / Submitted / Won / Lost |
| Proposal Directory | `proposals/[YYYYMMDD]-[agency]-[title]/` |
| Links | [SAM.gov link] / [Agency link] |
| Notes | |
```

---

## RFP Response Structure Template

Adapt to each RFP's specific requirements (Section L = instructions to offerors, Section M = evaluation criteria). Always read Section L in full before structuring the response.

### Volume I: Technical Volume

**Purpose:** Convince the technical evaluators you can do the work.

```
1.0 Executive Summary (if permitted)
    1.1 Understanding of the Requirement
    1.2 {{COMPANY}} Solution Overview
    1.3 Key Differentiators

2.0 Technical Approach
    2.1 [Task/Objective 1 from PWS/SOW]
        - Understanding the requirement
        - Proposed methodology
        - Tools, technology, equipment
        - Deliverables
    2.2 [Task/Objective 2]
    ...

3.0 Innovation / Technical Advantages
    3.1 [Primary Differentiator — describe {{COMPANY}}'s unique technology/approach]
    3.2 [Secondary Differentiator — describe additional competitive advantages]
    3.3 [Integration or platform advantages]

4.0 Risks and Mitigation
    4.1 Risk 1: [Description] | Likelihood: [H/M/L] | Impact: [H/M/L] | Mitigation: [Action]
    ...

5.0 Schedule / Work Breakdown Structure
    5.1 High-level milestone schedule
    5.2 WBS (if required)
```

### Volume II: Management Volume

**Purpose:** Show you can manage the contract, not just the technology.

```
1.0 Management Approach
    1.1 Project Organization
    1.2 Roles and Responsibilities
    1.3 Communication and Reporting Plan
    1.4 Quality Assurance Plan

2.0 Key Personnel
    2.1 [Name] — [Title/Role]
        - Relevant qualifications
        - Role on this contract
        - % time dedicated
    ...

3.0 Subcontractors / Teaming (if applicable)
    3.1 [Partner name] — [Role] — [Rationale for selection]

4.0 Facilities and Resources
    4.1 {{COMPANY}} Operations / HQ
    4.2 Partner facilities (if applicable)

5.0 Phase-In Plan (if applicable)
```

### Volume III: Past Performance

**Purpose:** Demonstrate you've done similar work and done it well.

```
For each reference (typically 3-5):

[Reference #]
Client: [Name / Agency]
Contract #: [If applicable]
Period of Performance: [Start] – [End]
Contract Value: $[Amount]
Work Description: [2-3 sentences — what {{COMPANY}} delivered]
Relevance: [1 sentence connecting this to the current requirement]
Outcome: [Measurable results]
Reference: [Name, Title, Phone, Email]
```

### Volume IV: Price / Cost Volume

**Purpose:** Competitive, defensible pricing that reflects real costs.

```
1.0 Price Summary Table
    | CLIN | Description | Unit | Qty | Unit Price | Total |

2.0 Labor Detail
    | Labor Category | Hours | Rate | Total |

3.0 Indirect Rates
    | Rate Type | Proposed Rate | Basis |

4.0 Cost Narrative
    4.1 Basis of Estimate
    4.2 Subcontract costs (if any)
    4.3 ODCs (materials, travel, equipment)

5.0 Total Evaluated Price
```

---

## Compliance Matrix Template

**Build this before drafting anything.** Every RFP requirement gets a row.

```markdown
# Compliance Matrix — [Title] ([Solicitation #])
Generated: [Date]

| # | Section | Requirement Summary | Vol | Section | Status | Notes |
|---|---------|---------------------|-----|---------|--------|-------|
| 1 | L.4(a) | Technical approach: describe methodology | I | 2.0 | Done | |
| 2 | L.4(b) | Past performance: 3 references | III | 1.0-3.0 | Done | |
| 3 | L.5 | Price in CLIN format | IV | 1.0 | Done | |
| 4 | L.7(a) | Page limit: 25 pages technical | I | — | Partial | Currently at 22pp |
| 5 | M.1 | Eval criterion: Technical 40% | — | — | Noted | Weight noted |
| 6 | L.9 | SF-33 required | Attch | A | Done | |

Status key:
Done = Addressed   Partial = Needs attention   Missing = Not yet addressed   Noted = Eval criterion
```

---

## Win Themes

<!--
  CUSTOMIZE THESE for {{COMPANY}}. These are templates — replace the bracketed
  content with {{COMPANY}}'s actual differentiators, tech, and positioning.
-->

These should appear across the Technical, Management, and Past Performance volumes — not once, but consistently. Evaluators score what they see; make them see it.

### Win Theme 1: [Unique Heritage / Pedigree]
> "{{COMPANY}}'s [technology/approach] was developed [origin story — e.g., in collaboration with leading research institutions, through decades of industry experience, etc.]. This heritage provides both technical rigor and institutional trust that competitors cannot match."

**Use when:** The opportunity values experience, pedigree, or institutional relationships.

### Win Theme 2: [Unique Technology / Capability]
> "{{COMPANY}}'s [proprietary technology/methodology] delivers [specific benefit] in conditions where conventional approaches fail. No other vendor in this space offers this capability."

**Use when:** The RFP requires capabilities where {{COMPANY}} has a clear technical edge.

### Win Theme 3: [Full Solution / Single Vendor]
> "{{COMPANY}} delivers a complete, integrated solution: [list components] — all from a single vendor. Agencies avoid the integration risk and split accountability that come with multi-vendor approaches. One point of contact. One SLA. One team responsible for outcomes."

**Use when:** The opportunity might consider piecing together a solution from multiple vendors.

### Win Theme 4: [Proven at Scale]
> "{{COMPANY}} has [specific metric — e.g., served X clients, processed Y transactions, deployed across Z facilities] in live engagements. This isn't a prototype or a pilot — it's a production-grade [system/service] operating at scale."

**Use when:** Past performance or capability demonstration sections. Quantify whenever possible.

### Win Theme 5: [Strategic Location / Proximity]
> "Based in [location], {{COMPANY}} operates in proximity to [relevant institutions, agencies, or clients]. Our team understands the operational environment and culture of this community."

**Use when:** Location is relevant to the opportunity.

---

## Standard Boilerplate Sources

When a proposal needs a standard section, pull from `knowledge/boilerplate/` first.

| Section Needed | Source File | Notes |
|----------------|-------------|-------|
| Company description | `boilerplate/company-description-250.md` | Have 100/250/500 word versions |
| Key personnel intro | `boilerplate/key-personnel-intro.md` | |
| Quality assurance | `boilerplate/quality-assurance.md` | Customize for each contract |
| Cybersecurity | `boilerplate/cybersecurity.md` | Verify against NIST/CMMC requirements each time |
| Equal opportunity | `boilerplate/eeo-statement.md` | Standard language, rarely changes |
| Registrations | `compliance/registrations.md` | SAM.gov UEI, CAGE code, etc. |

---

## Pre-Submission Review Checklist

Run this 24-48 hours before every submission. If any item fails, stop and fix before submitting.

### Compliance
- [ ] Compliance matrix complete — no missing items
- [ ] Page limits verified (exact page count, not estimated)
- [ ] Font size, margins, line spacing match RFP specs exactly
- [ ] File format correct (PDF, Word, or as specified)
- [ ] File naming convention matches solicitation requirements
- [ ] All required volumes present

### Content Accuracy
- [ ] All technical specs verified against internal documentation
- [ ] Past performance reference contacts confirmed reachable
- [ ] All cost figures cross-checked (minimum 2 independent checks)
- [ ] Win themes appear in technical, management, AND past performance volumes
- [ ] No confidential or proprietary info included without proper markings
- [ ] Technical claims are accurate and defensible
- [ ] Partnership/teaming language approved by {{USER_NAME}}

### Attachments and Forms
- [ ] All required forms complete (SF-33, SF-1449, reps and certs, etc.)
- [ ] SAM.gov registration active (check day-of)
- [ ] All certifications current
- [ ] Teaming agreements signed (if applicable)
- [ ] Letters of commitment attached (if required)

### Final
- [ ] {{USER_NAME}} has read and approved all volumes
- [ ] Submission portal login verified (don't discover a password issue at deadline)
- [ ] Time zone confirmed for deadline — Solicitations often specify Eastern time
- [ ] Backup submission plan identified (if portal fails)
- [ ] {{AGENT_NAME}} briefed on submission time for confirmation capture

---

## Key RFP Sources

### Federal — Primary
| Source | URL | Use |
|--------|-----|-----|
| SAM.gov | https://sam.gov | All federal solicitations — daily scan |
| SBIR.gov | https://sbir.gov | Cross-agency SBIR/STTR portal |
| DOE SBIR | https://science.osti.gov/sbir | Energy-specific SBIR solicitations |
| DoD SBIR | https://www.dodsbirsttr.mil | Defense SBIR/STTR — DARPA, Army, Navy, AF |

### Federal — Intelligence & Alerts
| Source | URL | Use |
|--------|-----|-----|
| GovWin IQ | https://iq.govwin.com | Pre-solicitation intelligence |
| USASpending.gov | https://usaspending.gov | Research past awards |
| FPDS | https://fpds.gov | Contract data |
| AFWERX | https://afwerx.com | Air Force commercial tech innovation |
| DIU | https://diu.mil | Defense Innovation Unit — commercial tech |

### DOE-Specific
| Source | URL | Focus |
|--------|-----|-------|
| ARPA-E | https://arpa-e.energy.gov | Advanced energy R&D |
| DOE OE | https://www.energy.gov/oe | Grid, energy delivery |
| DOE CESER | https://www.energy.gov/ceser | Cybersecurity, energy security |
| DOE EERE | https://www.energy.gov/eere | Efficiency, renewables |

### DHS / Critical Infrastructure
| Source | URL | Focus |
|--------|-----|-------|
| DHS S&T | https://www.dhs.gov/science-and-technology | Tech R&D for DHS missions |
| CISA | https://www.cisa.gov | Critical infrastructure protection |

### State / Regional
| Source | URL | Focus |
|--------|-----|-------|
| [Your State] Procurement | [State procurement portal URL] | State contracts |
| [Local SBA Office] | [URL] | Small business resources |

---

## SBIR/STTR Quick Reference

SBIR (Small Business Innovation Research) and STTR (Small Business Technology Transfer) are high-value funding mechanisms for technology-stage companies.

**SBIR Phase I:** Feasibility study — typically up to $200K, 6-12 months
**SBIR Phase II:** Full R&D — typically up to $1.5-2M, 2 years
**SBIR Phase III:** Commercialization — no set limit, non-SBIR funded
**STTR:** Like SBIR but requires a research institution partner

**Key agencies to target (customize for {{COMPANY}}):**

| Agency | Why |
|--------|-----|
| [Agency 1] | [Relevance to {{COMPANY}}'s technology/services] |
| [Agency 2] | [Relevance] |
| [Agency 3] | [Relevance] |
| [Agency 4] | [Relevance] |
| [Agency 5] | [Relevance] |

**SBIR strategy:**
- Phase I wins establish past performance
- Phase II + Phase III create sustained revenue streams
- STTR with research institution partners unlocks joint proposals

**Topic search approach:** Download each agency's open solicitation topics as PDF. Search for keywords relevant to {{COMPANY}}'s technology and capabilities. Flag topics where {{COMPANY}}'s offerings are a direct technical fit.

---

*Updated: [Onboarding date — update as playbook evolves]*
*Owner: {{AGENT_NAME}} (maintained) / {{USER_NAME}} (approved)*
