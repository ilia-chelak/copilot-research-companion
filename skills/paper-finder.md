# Paper Finder — Literature Search Capability

Research paper discovery and organization. Find relevant ML/AI/CV/NLP papers, organize them into a persistent knowledge base, and connect them across topics.

Adapted from [bchao1/paper-finder](https://github.com/bchao1/paper-finder).

---

## Directory Structure

All paper-search artifacts live under `literature/` at the repository root. Each search topic gets its own subfolder with a short, descriptive kebab-case name (e.g., `literature/mixed-resolution-diffusion/`). The user may also specify a custom folder name. Create on first use.

```
literature/
  <topic-name>/
    memory-bank.md        # Master list of all discovered papers
    mind-graph.md         # Topic → paper connection graph
    summaries/            # Per-paper .md summary files
    reviews/              # Per-paper OpenReview review files
    references.bib        # Combined BibTeX for all papers
    pdfs/                 # Downloaded PDFs (only when user asks)
```

If the user references an existing folder, operate within it. If starting a new search without a specified folder, derive a descriptive name from the search query.

---

## Searching for Papers

### Web search is mandatory

Use web search and web fetch for every search. Training knowledge alone misses recent papers. If web tools are denied, retry once, then tell the user you need web access and explain what you'd search for.

### Search strategy

Run 2–3 parallel searches per query:

1. **Semantic Scholar API** via web fetch: `https://api.semanticscholar.org/graph/v1/paper/search?query=<query>&limit=20&fields=title,authors,year,venue,abstract,externalIds,citationCount,url`
2. **Web search** with queries like `<topic> paper <venue> <year>` — good for Google Scholar results
3. **Venue-specific** when relevant: `<topic> CVPR 2025`, `<topic> site:openreview.net`
4. **Follow citations** on Semantic Scholar for highly relevant papers

Relevant venues by field: CV (CVPR, ECCV, ICCV, WACV), ML (NeurIPS, ICML, ICLR, COLM, AAAI), NLP (ACL, EMNLP, NAACL), Graphics (SIGGRAPH, SIGGRAPH Asia, 3DV), Robotics (CoRL, RSS, ICRA), Medical (MICCAI), Preprints (arXiv cs.CV/CL/LG/AI).

### Multi-angle search (mandatory)

A single concept can be described using very different vocabulary depending on the angle. After the initial direct-concept searches, you MUST run at least one additional search round covering these three angles. Skipping these is the #1 cause of missed papers.

1. **Cross-domain synonyms**: The same idea often has established names in adjacent fields. Before searching, brainstorm 2–3 alternative terms from related domains (graphics, neuroscience, signal processing, HCI, information theory, etc.). Search using these alternative vocabularies.

2. **Enabling mechanisms / building blocks**: Search for the specific technical components needed to *implement* the concept — not just the concept itself. Every novel representation requires changes to attention, positional encodings, loss functions, normalization, etc.

3. **Motivating applications / problem framing**: Papers solving the same technical problem may frame it as a different goal. Search from the perspective of *why* someone would build this (efficiency, speed, perceptual quality, hardware constraints).

After initial results come in, also **follow the citation graph**: fetch the related-work section of 1–2 top-relevance papers and scan for references you haven't found yet.

### Understand the concept precisely

Before searching, understand the exact technical distinction the user cares about. If they describe a specific mechanism, search for that literal property — don't broaden to superficially similar but technically different work.

### Filtering

- **Prioritize algorithmic contributions** over architecture/engineering/systems papers
- **Prioritize recent work** (2024–2025+) — skip well-known basics unless directly relevant
- **Note citation counts** when available
- **Tier results** by relevance to the user's specific concept

---

## OpenReview Review Lookup

### Why this matters

Paper abstracts are self-promotional — they highlight strengths and hide weaknesses. Peer reviews from OpenReview provide an objective counterbalance: they surface real weaknesses, questionable claims, and limitations that abstracts never mention. This makes your competitive landscape analysis, novelty assessment, and impact evaluation significantly more grounded.

### When to run

Run an OpenReview lookup for **every** discovered paper, not just top-relevance ones. A paper that looks strong from its abstract may have devastating reviews, and a paper that looks incremental may have reviewers praising a subtle but important contribution.

### Lookup protocol

For each discovered paper, use the `openreview_lookup.py` helper script as the **primary method**, with web search as fallback.

**Prerequisites:** Ensure `requests` is installed: `pip install -r requirements.txt`

**Step 1 — Primary: Use the helper script**

Run the lookup script via bash:

```bash
python scripts/openreview_lookup.py "<exact paper title>" --venue <VENUE> --year <YEAR>
```

Examples:
```bash
python scripts/openreview_lookup.py "TTT3R: 3D Reconstruction as Test-Time Training" --venue ICLR --year 2026
python scripts/openreview_lookup.py "Latent Radiance Fields with 3D-aware 2D Representations" --venue ICLR --year 2025
python scripts/openreview_lookup.py --forum-id aMs6FtNaY5
```

To save directly to a review file:
```bash
python scripts/openreview_lookup.py "<title>" --venue ICLR --year 2026 --output reviews/<short-id>.md
```

**Interpret exit codes:**
- `0` — Success. Reviews found and printed to stdout. Save output to `reviews/<short-id>.md`.
- `2` — Paper not found on OpenReview. Record `Review Status: not-on-openreview`.
- `3` — Paper found but no public reviews available. Record `Review Status: no-reviews-available`.
- `5` — API/auth/network error (the script prints guidance on stderr). Record `Review Status: lookup-failed`.

Always provide `--venue` and `--year` hints when known — this dramatically narrows the search and avoids false matches.

**Step 2 — Fallback: Web search (only if script fails with exit code 5)**

If the script fails due to API errors, fall back to web search:

1. Search: `site:openreview.net "<exact paper title>"`
2. If found, extract the forum ID from the URL and retry the script with `--forum-id`
3. If still failing, use web search to find review summaries: `openreview "<title>" reviews ratings strengths weaknesses`
4. If all approaches fail: record `Review Status: lookup-failed` with error details

### What to extract

**Paper-level metadata:**
- **Decision** (accept/reject/withdrawn, if visible on the page)
- **Meta-review** (area chair summary and recommendation, if present)

**Per-reviewer content** — extract the **complete** review from each official reviewer:

- **Reviewer ID** (e.g., Reviewer 1, Reviewer 2, etc.)
- **Rating** (preserve the exact rating text verbatim, e.g., "6: marginally above acceptance threshold" or "5/10" — do NOT normalize to a /10 scale since scales vary by venue and year)
- **Confidence** (if available)
- **Summary** (reviewer's summary of the paper)
- **Strengths** (full text — every point the reviewer lists)
- **Weaknesses** (full text — every point the reviewer lists)
- **Questions** (questions to authors, if any)
- **Limitations** (if the reviewer has a separate limitations section)
- Any additional review fields present (e.g., "Soundness", "Presentation", "Contribution") — preserve them under their original field names

Note: Review schemas vary across venues and years. Prefer the normalized sections above when the fields map cleanly, but if a review uses different field names, preserve the original structure rather than force-fitting it.

### Where to store reviews

Write the full review content to a dedicated file: `reviews/<short-id>.md`

Format:

```markdown
# OpenReview Reviews: [Paper Title]
- **OpenReview URL**: https://openreview.net/forum?id=<FORUM_ID>
- **Decision**: Accept / Reject / Withdrawn (if known)
- **Ratings**: Reviewer 1: [verbatim], Reviewer 2: [verbatim], ... (N reviewers)

---

## Reviewer 1
- **Rating**: [verbatim rating text, e.g., "6: marginally above acceptance threshold"]
- **Confidence**: [verbatim, if available]

### Summary
[Full reviewer summary]

### Strengths
[Full text of all strengths]

### Weaknesses
[Full text of all weaknesses]

### Questions
[Full text of questions to authors]

### [Any Additional Fields]
[Preserve non-standard review fields under their original names]

---

## Reviewer 2
[Same structure]

---

## Meta-Review (if available)
[Area chair summary and recommendation]
```

If review fields don't map cleanly to the sections above (different venue schema), use a `### Raw Review` section and preserve the original field names and content verbatim.

### Handling edge cases

- **Paper not on OpenReview**: Record `Review Status: not-on-openreview` in the memory bank. Only use this status when web search returned zero plausible matches — not when fetching failed.
- **Lookup failed** (403, timeout, rate limit, blocked): Record `Review Status: lookup-failed` with a brief error note (e.g., "API returned 403"). This is different from "not on OpenReview" — the paper may have reviews but access failed. Retry on next search session if the paper comes up again.
- **OpenReview page exists but no reviews**: Some papers are posted as submissions but reviews haven't been released yet. Record `Review Status: no-reviews-available`.
- **Workshop papers**: May have lighter reviews. Still extract what's available.
- **Venue coverage**: ICLR, NeurIPS, ICML, AAAI, and COLM consistently use OpenReview. ACL, EMNLP, and NAACL may have OpenReview threads via the ARR (ACL Rolling Review) pipeline — still attempt lookup. CVPR, ECCV, ICCV, and SIGGRAPH generally do not use OpenReview, but attempt lookup anyway since the web search will simply return no results.

### Batch efficiency

When looking up many papers, run the script sequentially for each paper (one call per title). Prioritize papers from venues known to use OpenReview (ICLR, NeurIPS, ICML, AAAI, COLM) first, since they're most likely to have results, but still attempt all papers.

Use `--output` to write directly to review files:
```bash
for each paper:
    python scripts/openreview_lookup.py "<title>" --venue <V> --year <Y> --output reviews/<short-id>.md
```

The script handles all the API complexity (venue invitation formats, review field schemas, error handling). You just need to provide titles and interpret exit codes.

---

## Memory Bank (`memory-bank.md`)

Master record of all discovered papers. Append new entries, never overwrite existing entries. However, **updating metadata fields** on an existing entry is allowed and expected — e.g., adding review status after an OpenReview lookup, or updating citation counts. Read existing file before searching to avoid duplicates.

Existing entries from before the OpenReview integration may lack review fields — treat missing review fields as `unknown` and backfill when the paper is revisited in a future search.

```markdown
# Paper Memory Bank
Last updated: YYYY-MM-DD

### [short-id] Paper Title
- **Authors**: Author list
- **Venue**: Conference/Journal, Year
- **URL**: Link to paper
- **Citations**: N (if known)
- **Status**: discovered | summarized | analyzed
- **Topics**: topic1, topic2
- **Abstract**: 1-2 sentence description
- **Notes**: Relevance observations
- **Review Status**: reviewed | not-on-openreview | no-reviews-available | lookup-failed
- **OpenReview URL**: link to forum page (if reviewed)
- **OpenReview Rating**: verbatim ratings per reviewer (if reviewed)
- **Reviews File**: reviews/<short-id>.md (if reviewed)
---
```

## Mind Graph (`mind-graph.md`)

Topic-centric hierarchy — NOT pairwise paper comparisons. Each topic has 1–3 umbrella/landmark papers plus other relevant work.

```markdown
# Mind Graph
Last updated: YYYY-MM-DD

### Topic Name
- **Description**: One-line description
- **Related topics**: [other topic], [other topic]
- **Key papers**:
  - [short-id] Paper Title (Venue Year) — why it's key for this topic
- **Other relevant papers**:
  - [short-id] Paper Title — one-line note
```

## BibTeX (`references.bib`)

Write a single combined `references.bib` file with all papers. Use `@inproceedings` for conferences, `@article` for journals, `@misc` for arXiv preprints. Citation key = short-id.

## Paper Summaries

When the user asks for a deeper summary of a specific paper, write a summary to `summaries/<short-id>.md` containing: title, authors, venue, one-paragraph TL;DR, key contributions (bulleted), method overview, results highlights, limitations, and relevance to the user's research.

Only create summaries when the user explicitly asks — don't auto-summarize during search.

## PDF Management

Do NOT download PDFs unless the user explicitly asks. When asked:

1. Read `references.bib` to extract the arXiv eprint ID or URL for each paper.
2. Construct the PDF URL from the arXiv ID: `https://arxiv.org/pdf/<eprint-id>`
3. Download via curl and save to `pdfs/<short-id>.pdf`
4. Only fall back to web search if a paper has no entry in references.bib.

---

## Interaction Flow

1. **Search**: Run parallel web searches, present ranked list (title, venue, year, citations, one-line description)
2. **Record**: Add papers to memory-bank.md, update mind-graph.md, write references.bib
3. **Review Check**: For every discovered paper, run the OpenReview lookup protocol. Update memory-bank entries with review status and ratings. Write full reviews to `reviews/<short-id>.md` for papers that have them. When presenting results to the user, flag papers with notably low or high reviewer ratings.
4. **Ask**: Whether user wants deeper analysis of any specific papers — now informed by reviewer perspective

---

## Usage by Other Roles

When invoked as a support capability by other agents (Idea Critic, Research Strategist, Brainstormer), **always persist results** — every paper discovered during any interaction must be recorded in the memory bank, mind graph, and references.bib. This is non-negotiable even for quick competitive-landscape lookups. The memory bank is the long-term knowledge base; skipping persistence means losing work.

**Leveraging review data in evaluations:**

When other agents consume paper finder results, they should actively use the OpenReview review data:

- **Idea Critic**: Full reviewer weaknesses on competing papers reveal exploitable gaps in the landscape, or indicate the problem is harder than abstracts suggest. A competing paper with harsh reviews may be less threatening than it looks; a paper with glowing reviews confirms the direction is viable but the bar is high.
- **Research Strategist**: Low reviewer ratings + specific weaknesses on "competing" papers may mean the competitive landscape is weaker than it appears from abstracts alone. High ratings confirm a paper is as strong as claimed. Scooping risk is lower when the "scooping" paper has serious reviewer concerns.
- **Brainstormer**: Reviewer weaknesses on papers in a problem space point to unresolved challenges and open problems — prime territory for new ideas.
