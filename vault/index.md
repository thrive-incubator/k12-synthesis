---
type: index
last_updated: 2026-W27
---

# Thrive Center K12 Knowledge Vault

This vault is the Thrive Center Incubator's internal knowledge base for the **K12 edtech
funding ecosystem**, with a deliberate weighting toward **student wellbeing and mental health**.
It tracks how federal dollars and policy flow down through state systems, district purchasing,
and the charter sector into the technology/vendor layer and the ideas/influence layer — so that
staff can see where ideas that produce positive wellbeing outcomes can take root inside the real
funding framework. It is fed once a week by the `k12-synthesis` skill, whose synthesized digest
is the raw material this vault accretes into durable, pre-synthesized knowledge. The markdown
files here are the source of truth (versioned in git) and are designed to be navigated by an AI
agent: read this file first, filter on front-matter, read entity/theme pages for synthesized
arcs, and read specific digests only when you need week-level detail.

## How to navigate

The vault has **two axes**:

1. **Chronological digests** (`digests/`) — the weekly synthesis output, append-only raw
   material. One file per ISO week (e.g. `digests/2026/2026-W26.md`). Read these for the detail
   of a specific week.
2. **Accreting entity & theme pages** (`entities/`, `themes/`) — the actual *knowledge*, built
   up over time so longitudinal questions ("what's the 18-month arc of school Medicaid funding,
   and who's positioned for it?") can be answered from a pre-synthesized page instead of
   re-derived from scratch. Each page carries a mutable **Current snapshot** and an append-only
   **Timeline**.

Read order for an agent answering a question: **this file → relevant entity/theme page(s) for
the synthesized arc → specific digest(s) only for week-level detail.** Filter on front-matter
(`layers`, `entities`, `states`, `tags`) to narrow before reading bodies.

The full operating manual — schemas, naming, provenance rules, and the weekly update procedure —
is in [CONVENTIONS.md](CONVENTIONS.md). The controlled vocabulary (six layers + canonical tags +
naming rules) is in [TAGS.md](TAGS.md).

## Active themes

Each theme links to its page in `themes/`.

- [School Mental Health Funding — State vs Federal Reliability](themes/school-mental-health-funding.md) — states stepping in as federal school-mental-health money wobbles.
- [Enrollment Decline & District Consolidation](themes/enrollment-decline-consolidation.md) — shrinking per-pupil revenue and the resulting school closures.

## Tracked entities

Grouped by type; each entity links to its page in `entities/`.

### Companies

- [Educational Testing Service (ETS)](entities/companies/ets.md) — assessment giant; acquired ACT (2026-W27).
- [ACT](entities/companies/act.md) — assessment organization; acquired by ETS (2026-W27).

### Agencies

- [U.S. Department of Education](entities/agencies/us-department-of-education.md) — federal education funding, special education, school choice.
- [SAMHSA](entities/agencies/samhsa.md) — federal behavioral/mental-health grant funder.
- [HRSA](entities/agencies/hrsa.md) — federal pediatric health-access grant funder.

### Programs

- [Trauma-Informed Services in Schools](entities/programs/trauma-informed-services-in-schools.md) — SAMHSA grant (SM-26-006), closes July 16, 2026.
- [Pediatric Mental Health Care Access Program (PMHCA)](entities/programs/pediatric-mental-health-care-access-program.md) — HRSA grant, closes July 10, 2026.
- [Florida Mental Health Assistance Allocation](entities/programs/florida-mental-health-assistance-allocation.md) — state school-mental-health funding vehicle.

## Digests by week

Each week links to its file in `digests/`, newest first.

- [2026-W27](digests/2026/2026-W27.md) — Jun 24 – Jul 1, 2026: Maryland's $96M vs Maine's frozen federal funds; ETS acquires ACT; SAMHSA school-trauma grant open.
