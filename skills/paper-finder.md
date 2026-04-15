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

## Memory Bank (`memory-bank.md`)

Master record of all discovered papers. Append new entries, never overwrite. Read existing file before searching to avoid duplicates.

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
3. **Ask**: Whether user wants deeper analysis of any specific papers

---

## Usage by Other Roles

When invoked as a support capability by other agents (Idea Critic, Research Strategist, Brainstormer), **always persist results** — every paper discovered during any interaction must be recorded in the memory bank, mind graph, and references.bib. This is non-negotiable even for quick competitive-landscape lookups. The memory bank is the long-term knowledge base; skipping persistence means losing work.
