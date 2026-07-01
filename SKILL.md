---
name: k12-synthesis
description: >-
  Generate the weekly Thrive Center K12 synthesis: a research briefing that maps the K12 funding ecosystem — federal dollars and policy flowing down through state systems, district purchasing, and the charter sector, into the technology/vendor layer and the ideas/influence layer — with a deliberate weighting toward student wellbeing and mental health. The goal is to help a time-poor Thrive Center researcher see how ideas that produce positive wellbeing outcomes can take root inside the real funding framework. Fetches a fixed set of no-auth RSS feeds, Google News topic queries, and public JSON APIs directly, keeps facts mostly raw with a thin layer of synthesis on top, organizes everything into six layers, and writes the result as a markdown file. Use whenever the user asks for the weekly Thrive synthesis, the K12 funding/wellbeing landscape, the Thrive Center briefing, a "this week in K12 funding & wellbeing" roundup, or wants to regenerate, refresh, or rerun the synthesis — even for terse asks like "run the synthesis" or "what moved in K12 this week."
---

# Thrive K12 Funding & Wellbeing Synthesis

## What this produces

A single markdown file: a weekly research briefing for a Thrive Center member who is smart
and domain-aware but does not have time to keep up with K12 news, and who would miss things
without this automation. The purpose is research, not a newsletter.

The throughline of the work: **understand the K12 funding ecosystem — how federal money and
policy flow down through states, districts, and charter schools into vendors and ideas — well
enough to see where ideas that produce positive student-wellbeing outcomes can actually take
root inside that framework.** Track the whole machine, but keep a deliberate weighting toward
student wellbeing and mental health.

That purpose drives the tone:

- **Keep facts raw.** A researcher needs to trust and verify the underlying fact. Report what
  happened, with the key numbers, names, dollar figures, and dates intact and in the source's
  terms — not paraphrased into mush. Always link the source.
- **Thin synthesis on top, not instead.** Layer analysis lightly: a "So what" line where an
  item genuinely connects to the funding stack or to wellbeing, and one synthesis section at
  the top that ties the week together. Don't bury the facts under interpretation.
- **Straight to the point.** No padding, no press-release rewriting, no throat-clearing. If the
  week was quiet, say so and keep it short.

The output is markdown by design so it can be converted to a .docx later. Keep the markdown
clean and conversion-safe (see Markdown conventions).

## How this works

Two layers, split on purpose: **deterministic plumbing in code, judgment in the model.**

- **`ingest.py` (the plumbing)** fetches every no-auth source, parses RSS/Atom/JSON, filters news
  to the window, filters grants to those open/closing soon, dedupes, and writes `candidates.json`
  — a compact (~9k-token) list of candidate items. It is stdlib-only (no pip installs) and runs
  the same way every week, so the ingestion is reproducible and a single bad feed can't silently
  drop coverage (it's reported loudly instead). This replaces ~800k tokens of raw XML that would
  otherwise have to be read into context.
- **You (the judgment)** read `candidates.json` and do the part that can't be coded: apply the
  relevance bar, assign layers, dedupe across wire copies, write the raw-fact-plus-"So what"
  items, and synthesize the throughline. Lean on your judgment here; the script never makes an
  editorial call.
- **Links stay in code, never in your prose.** Every candidate in `candidates.json` carries a short
  `ref` (e.g. `n012`, `o03`, `fr1`). When you cite a source you write that token — `[link]({{n012}})` —
  **never a URL.** A URL is an opaque string (article ids, redirect blobs) you cannot reproduce from
  memory; if you type one from your understanding of an item, you will sooner or later emit a
  plausible-but-wrong link that looks correct and passes every eyeball check. So don't type URLs at
  all. `assemble.py` (step 9) swaps each `{{ref}}` for its exact link and rejects any hand-typed URL
  or unknown token, so a fabricated link cannot reach the final file.

If `ingest.py` can't run (e.g. no Python), fall back to fetching sources directly with curl —
but that's the exception, not the design. Even in the fallback, cite the exact URL you actually
fetched; never reconstruct a URL from a headline.

## Workflow

1. **Set the window.** Default to the trailing 7 days ending today; if the user names a different
   range, use it. State the window at the top of the synthesis.
2. **Run the ingest script** from the skill directory:
   ```
   python3 ingest.py --end <YYYY-MM-DD> --out /tmp/candidates.json
   ```
   (Omit `--end` for today; use `--days N` for a non-7-day window.) Read its stderr summary —
   **if it lists sources as "degraded or unavailable," note them for the footer; that's a real
   coverage gap, not a detail to skip.**
3. **Read `candidates.json`.** It has `news` (each with a `layer_hint`), `opportunities`
   (grants, sorted by soonest close), `federal_register`, and `unavailable`.
4. **Filter for relevance.** Apply the bar in What counts. Be strict — a synthesis of 12–18 sharp
   items beats 40 where half are noise. The script errs toward recall; you supply the precision.
   Cutting a marginal item is the safer error. A few international/higher-ed items still slip past
   the query exclusions — drop them here.
5. **Sort into the six layers.** Use `layer_hint` as a starting suggestion, not a verdict —
   reassign by where the funding logic is clearest. If an item fits two, place it once.
6. **Dedupe across sources.** The script dedupes by title, but near-duplicate wire stories under
   different outlets still slip through — collapse them, citing the most original/detailed.
7. **Write each item** in the standard item format: raw fact first, optional "So what" line. Cite
   each source with that item's `{{ref}}` token from `candidates.json` — never a typed URL.
8. **Write "This Week's Throughline" last**, once every layer exists — it is the synthesis pass.
9. **Assemble, then save.** Write your draft (with `{{ref}}` tokens, no URLs) to a file, then expand
   and verify the links:
   ```
   python3 assemble.py --candidates /tmp/candidates.json --draft <draft>.md --out <final>.md
   ```
   `assemble.py` replaces every token with its exact link and **fails if it finds any hand-typed URL
   or unknown token**, so a fabricated link cannot reach the final file. Read its stderr ref→source
   map to confirm tokens point at the items you meant; fix any error it reports (re-cite the token —
   do **not** hand-edit a URL in) and re-run. Include unavailable sources in the footer, then tell
   the user where the final file is.

## The layers

Six layers, following the money from source to outcome. Use these exact section headings; omit
any layer with no qualifying items rather than printing an empty heading.

1. **Federal Funding & Policy** — formula grants, competitive grants, regulations, guidance, and
   appropriations out of ED, HHS/SAMHSA, and related agencies. The top of the funnel: dollars
   and rules that everything downstream inherits.
2. **State Systems** — how federal dollars become state allocations, state plans, Medicaid and
   state-funded school mental health, and the policy implementation that decides what reaches
   districts. The translation layer.
3. **District Purchasing Layer** — district budgets, contracts, procurement, RFPs, and staffing
   decisions. Where money becomes a buying decision.
4. **Charter School Sector** — public funding flows, management/CMO contracts, vendor purchasing,
   and innovation pilots in the charter sector. A distinct buying and experimentation channel.
5. **Technology & Vendor Layer** — software, screening and assessment tools, telehealth, SEL
   platforms, and compliance tools — plus the companies behind them (funding, launches, M&A,
   shutdowns). Where ideas become products that districts and charters buy.
6. **Ideas & Influence Layer** — research, evidence, evaluations, advocacy, and narratives that
   shape what the field believes works. Where wellbeing ideas gain (or lose) legitimacy before
   the money follows.

## What counts (relevance bar)

The reader's time is the scarce resource. Two things earn an item a slot, and the best items do
both:

- **It moves the funding ecosystem** — money, policy, purchasing, or staffing that changes what
  flows through any layer of the K12 stack.
- **It touches student wellbeing or mental health** — SEL, screening, school-based mental health,
  counseling, telehealth, youth wellbeing.

Weight the two. The intersection — *wellbeing money and policy* — is the gold; lead with it.
Also include major general-ecosystem moves (a big federal appropriation shift, an ESSER-cliff
consequence, a major district budget action) even when not wellbeing-specific, because they
change the framework wellbeing ideas must live in. And include notable wellbeing items —
research, a new model, an evaluation — even when the dollars are small, because this is research.

**Filter out:** generic teaching tips, lesson plans, and PD content; sports, facilities, and
board politics with no funding or wellbeing angle; higher-ed-only or international-only stories
with no K12 relevance; and all-of-government grants or federal-register notices unrelated to
education or youth health. When unsure, leave it out.

## Sources (all no-auth)

`ingest.py` fetches everything below — you don't fetch these by hand. This section documents what
the script covers and how to edit it (the source lists live in clearly-marked constants at the top
of `ingest.py`: `FEEDS`, `GN_QUERIES`, `FR_QUERIES`, `GRANTS_KEYWORDS`). When you change a source
here, change it there.

### Layer-spanning RSS feeds (`FEEDS`)

These feed multiple layers; each carries a `layer_hint` the model can override during curation.

| Source | Feed | Feeds mainly |
| --- | --- | --- |
| K-12 Dive | https://www.k12dive.com/feeds/news/ | Federal, State, District — best all-rounder for funding/policy/procurement. |
| EdSurge | https://www.edsurge.com/articles_rss | Vendor, Ideas. Filter out general teaching & PD. |
| EdTech Insiders | https://edtechinsiders.substack.com/feed | Vendor — funding rounds, M&A, launches. Some higher-ed/global to filter. |
| The 74 | https://www.the74million.org/feed/ | Charter, Federal, Ideas — strong charter and policy coverage. |
| Chalkbeat | https://www.chalkbeat.org/arc/outboundfeeds/rss/ | State, District — strong local/state bureaus. High volume; filter hard. |
| Hechinger Report | https://hechingerreport.org/feed/ | Ideas, District — research-leaning education journalism. |
| Education Commission of the States | https://www.ecs.org/feed/ | State, Ideas — state policy analysis and briefs. |

*Dropped: Child Trends — its feed went permanently 404/504 (intermittent at best); the Ideas layer
is covered by Hechinger, The 74, ECS, and the Ideas Google News query. Re-add to `FEEDS` if it
comes back.*

### Google News topic queries (RSS, no-auth)

These are the targeted instrument — use them for the wellbeing weighting and for layers without
a dedicated feed (especially State, Charter, and federal wellbeing funding). Pattern:

```
https://news.google.com/rss/search?q=<URL-ENCODED QUERY>&hl=en-US&gl=US&ceid=US:en
```

Each `<item>` has `title`, `link`, `source`, and `pubDate`. Apply the trailing-7-day window to
`pubDate`. Expect heavy duplication of wire stories — dedupe aggressively. Run this standing set,
and add or adjust queries when a thread is developing.

**Two rules learned from live runs — apply them or the results are noisy:**

- **Always append the exclusion suffix** `-university -college -campus -"higher ed" -Australia -India -UK -"New Zealand"` to every query. Without it, these queries pull a flood of higher-ed and non-US (Australian/Indian/UK/NZ) budget and school stories that are off-target. Google News honors `-term` exclusions; quote multi-word phrases to keep them intact.
- **Do NOT use `when:7d`.** It silently zeroes out low-volume queries (the SAMHSA query returned 50 items without it and 0 with it). Fetch without a time operator and filter by `pubDate` in code instead — that's reliable and never drops a real hit.

The query column below shows the *core* terms; append the exclusion suffix above to each before
URL-encoding.

| Layer | Query core (decoded — add exclusion suffix) |
| --- | --- |
| Federal | `"school based mental health" funding OR grant "Department of Education"` |
| Federal | `SAMHSA OR "Department of Education" youth mental health schools grant` |
| State | `state Medicaid "school mental health" students` |
| State | `state budget "student mental health" public schools` |
| District | `"school district" contract OR RFP "mental health"` |
| District | `"school district" budget counselors OR therapists "mental health"` |
| Charter | `"charter school" mental health OR wellbeing students` |
| Charter | `"charter school" OR "charter management" funding OR grant` |
| Vendor | `"student mental health" software OR screening OR telehealth "school district"` |
| Vendor | `SEL OR "social emotional" platform OR app schools funding OR launch` |
| Ideas | `"student wellbeing" OR "youth mental health" study OR report OR evaluation schools` |

Curation still matters: a few international or higher-ed items will slip past the exclusions —
drop them by source/headline during filtering.

### Public JSON APIs (no-auth)

**Federal Register** (GET, returns JSON) — surface federal regulatory and grant-notice actions.
Low-volume by design — most weeks it returns nothing for school-mental-health terms, and that's
expected, not a failure. Keep running it every week anyway: when it *does* hit (a new rule, a
grant notice, a guidance withdrawal), it's a high-signal top-of-funnel event worth leading with.
Run a few queries varying term + agency, filtered to the window:

```
https://www.federalregister.gov/api/v1/documents.json?per_page=20&order=newest&conditions[publication_date][gte]=YYYY-MM-DD&conditions[term]=school%20mental%20health&conditions[agencies][]=education-department
```

Useful term → agency pairings: school mental health / student wellbeing → `education-department`
and `health-and-human-services-department`; substance use / youth behavioral health →
`substance-abuse-and-mental-health-services-administration`; Medicaid in schools →
`centers-for-medicare-medicaid-services`. Each result has `publication_date`, `agencies`,
`type`, and `html_url`.

**Grants.gov** (legacy no-auth endpoint, POST) — open federal funding opportunities. Scope by
keyword or it returns all-of-government:

```
curl -s -X POST https://api.grants.gov/v1/api/search2 \
  -H "Content-Type: application/json" \
  -d '{"keyword":"school mental health students","oppStatuses":"forecasted|posted","rows":25}'
```

Confirm the response path (`data.oppHits`) and field names against a live response the first
time you run it; the legacy schema can drift. Also try keywords `student wellbeing`,
`youth behavioral health`, and `SEL schools`.

### Known-blocked sources (route around via Google News)

These block automated fetches (403) or no longer expose a usable feed. Do not fetch them
directly; their coverage is recovered through the Google News queries above:

- **Behavioral Health Business** (youth mental-health vendors/telehealth) → Vendor queries.
- **National Alliance for Public Charter Schools** → Charter queries + The 74.
- **Brookings / FPF Student Privacy Compass** → Ideas and Federal queries.
- **ED.gov** (no real RSS) → Federal Register API + Federal queries.

## Known blind spots (state these in the synthesis when relevant)

The instrument is honest about what it can't see. Two layers are structurally under-covered
because no clean no-auth source exists, and you should not mistake a quiet week there for nothing
happening:

- **State Systems (mechanics).** "How federal dollars become state allocations" — state plan
  amendments, Medicaid school-services policy, allocation formulas — lives in state agency sites,
  NASBO, and Medicaid bulletins, none of which are ingested. We catch state news via journalism
  (Chalkbeat, The 74, ECS, Google News), not the allocation machinery itself.
- **District Purchasing (the actual buying).** Real procurement signals — RFPs, contract awards,
  board-agenda line items — live on paid bid boards (GovSpend, BidNet) and district portals. We
  infer demand from budget-cut *journalism*, not observed *purchasing*.

When the synthesis leans on either layer, say what's inferred vs. observed. Closing these gaps
would require a paid data source — a deliberate future decision, not a bug to fix silently.

## Dates and windows

The one place sources behave differently, and getting it wrong is the classic mistake.

- **News sources** (RSS feeds, Google News) → include items whose publication date falls in the
  trailing 7 days.
- **Opportunity sources** (Grants.gov, Federal Register grant notices) → not "published this
  week"; they have open/close dates. Include an opportunity if it is open now, or opening or
  closing within ~60 days. Sort by closing date, soonest first, and flag anything closing within
  14 days. This is deliberately decoupled from the 7-day news window.

## Output format

```markdown
# Thrive K12 Funding & Wellbeing Synthesis
### Week of {start_date} – {end_date}

## This Week's Throughline
{3–6 tight sentences or bullets: the synthesis pass. Where did money and policy move this week,
and what does it imply downstream for student-wellbeing ideas trying to take root? Name the most
consequential items and connect them across layers. This is the one place you synthesize freely.
Write it last.}

## Federal Funding & Policy

### {Raw headline — what happened, in the source's terms}
*{Source} · {Month DD, YYYY}* · [link]({{ref}})

{1–2 sentences. Keep the key facts raw: dollar amounts, program names, agencies, dates.}

**So what:** {one line, only where it earns it — tie to the funding stack or to wellbeing. Omit
if the fact speaks for itself.}

---

{...repeat per item, then the other layers in order: State Systems, District Purchasing Layer,
Charter School Sector, Technology & Vendor Layer, Ideas & Influence Layer...}

## Open Funding Opportunities (wellbeing-relevant, open / upcoming)

### {Solicitation / grant title}
*{Agency / program} · Opens {date}* · **Closes {date}** · [link]({{ref}})

{What it funds and, if known, who's eligible. Note "⚠ closes in {N} days" if within 14.}

---
*Sources unavailable this run: {list, if any}.*
```

`{{ref}}` is a literal citation token — the candidate's `ref` from `candidates.json`, expanded to
the real link by `assemble.py`. **Every** link uses one, including secondary sources cited inline
inside an item (e.g. collapsing a wire duplicate): write `(also: [Source, date]({{n034}}))`, never a
typed URL. If a fact has no `ref`, it has no verifiable source — leave it out.

If it was a genuinely light week, say so plainly in This Week's Throughline and keep the
synthesis short. Never pad with marginal items to hit a length.

## Markdown conventions (so it converts cleanly to .docx later)

- Use ATX headings (`#`, `##`, `###`) — these map directly to Word heading styles.
- Standard bullet lists and `**bold**` / `*italic*` only. Plain `[text](url)` links.
- **Never nest a link inside an emphasis span.** Close the italic *before* the link —
  `*{Source} · {date}* · [link]({url})`, not `*{Source} · {date} · [link]({url})*`. A link
  wrapped in `*…*` is mis-parsed by Obsidian-style renderers (it prepends a stray `_` and the
  link won't open). Same rule for bold: keep `**Closes {date}**` and the link outside the italic.
- No raw HTML, no nested tables, no multi-level bullet gymnastics — those break in
  markdown-to-docx conversion.

## Edge cases

- A source is down or its URL moved: try the bash/curl fallback, then a Google News query on the
  same topic; if still unreachable, list it in the footer ("Sources unavailable this run: …")
  and continue. One dead source never blocks the synthesis.
- Google News duplication: the same wire story appears under many outlets. Keep the most original
  or detailed, collapse the rest.
- Ambiguous dates: prefer the publication date in the feed item; if there is none, use the best
  available timestamp and don't agonize.
- Paywalled or thin content: summarize from the feed entry itself; don't fabricate detail you
  can't see. To go deeper on one important story, fetch that specific article directly.
- Don't over-synthesize. If you can't draw a real connection to the funding stack or wellbeing,
  leave the "So what" off and let the raw fact stand.
