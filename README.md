# Research Companion for GitHub Copilot

**Strategic research thinking for [GitHub Copilot](https://github.com/features/copilot)** — idea evaluation, project triage, and structured brainstorming to help you do research that matters.

Most AI writing tools help you *write* papers. This helps you decide *which* papers to write.

Adapted from [andrehuang/research-companion](https://github.com/andrehuang/research-companion) (kudos!) which is a Claude Code plugin. Since copilot can be used for free and has a student subscription, I believe it is more approachable than a Claude plugin. Inspired by Nicholas Carlini's essay ["How to Win a Best Paper Award"](https://nicholas.carlini.com/writing/2026/how-to-win-a-best-paper-award.html).

## The Problem

Researchers don't lack the ability to write papers. They lack a trusted colleague who will:

- Tell them an idea isn't worth 6 months of their life — *before* they invest those months
- Ask "who else is working on this and what's your unfair advantage?"
- Challenge them to state the key insight in one sentence (and refuse to move on until they can)
- Help them find the unexpected cross-field connection that makes a contribution truly novel
- Evaluate whether a struggling project should be continued, pivoted, or killed

This project provides that colleague.

## Installation

Clone or copy this repo as a subdirectory of your research workspace:

```bash
cd /path/to/your/research
git clone <this-repo-url> research-companion
```

When you run Copilot from any parent directory containing `research-companion/`, it will automatically pick up the instructions from `.github/copilot-instructions.md`.

Alternatively, symlink or copy the `.github/copilot-instructions.md` into your own project's `.github/` directory to activate the research companion in any repo.

## What's Inside

### Roles

| Role | File | What it does |
|------|------|-------------|
| **Idea Critic** | `agents/idea-critic.md` | Stress-tests research ideas along 7 dimensions: novelty, impact, timing, feasibility, competitive landscape, the nugget, and narrative potential. Returns a Pursue / Refine / Kill verdict. |
| **Research Strategist** | `agents/research-strategist.md` | Project-level strategic thinking — triage (continue/pivot/kill), comparative advantage mapping, impact forecasting, opportunity cost analysis, and scooping risk assessment. |
| **Brainstormer** | `agents/brainstormer.md` | Creative brainstormer with explicit focus on cross-field connections, "strategic ignorance" (challenging flawed assumptions the field follows uncritically), and the skeptical-reader test. |

### Full Ideation Session

| Prompt | File | What it does |
|--------|------|-------------|
| **Research Companion** | `prompts/research-companion.md` | A structured multi-phase ideation session: **Seed** → **Diverge** → **Evaluate** → **Deepen** → **Frame** → **Decide**. Includes Carlini's "conclusion-first test." |

### Principles

8 research strategy principles organized into three categories (Problem Selection, Execution Strategy, Strategic Positioning) that guide the evaluations. See `principles/research-strategy.md`.

## Usage

### Evaluate a research idea

Just describe your idea and ask for evaluation:

```
I'm thinking about studying how LLM-generated code introduces subtle security
vulnerabilities that pass standard code review. Can you evaluate this idea?
```

The **Idea Critic** role will evaluate across 7 dimensions and give you a verdict with the single most important question to resolve next.

### Decide whether to continue a project

```
I've been working on adversarial attacks against multimodal models for 3 months.
I have some results but they're incremental. Two other groups just posted preprints
in the same area. Should I continue?
```

The **Research Strategist** will assess your competitive position, impact potential, and opportunity cost, then recommend Continue / Pivot / Kill.

### Run a full brainstorming session

```
I want to run a full research brainstorming session. I'm interested in the
intersection of program synthesis and scientific discovery.
```

This launches a 6-phase guided session:

1. **Seed** — Understand your problem space, interests, and what bugs you about the field
2. **Diverge** — Generate ideas, alternative framings, and cross-field connections
3. **Evaluate** — Stress-test the top 2-3 ideas with the Idea Critic
4. **Deepen** — Check novelty, positioning, and competitive landscape
5. **Frame** — Write the abstract and conclusion as if the paper is done (the conclusion-first test)
6. **Decide** — Final assessment with next steps

### Find cross-field connections

```
I work on differential privacy. What ideas from other fields
(cryptography, economics, ecology, etc.) could lead to novel approaches?
```

### Stress-test with a skeptical reviewer

```
Here's my draft abstract. Play devil's advocate — what would a skeptical
Area Chair say?
```

## The 7 Evaluation Dimensions

| # | Dimension | Key Question |
|---|-----------|-------------|
| 1 | **Novelty** | If you don't do this, how long until someone else does? |
| 2 | **Impact** | Can you write a compelling conclusion *right now*, without doing the work? |
| 3 | **Timing** | Is the field ready for this? Too early? Already crowded? |
| 4 | **Feasibility** | What's the single riskiest assumption? Can you test it in a week? |
| 5 | **Competitive Landscape** | Who else is working on this? What's your unfair advantage? |
| 6 | **The Nugget** | Can you state the key insight in one sentence? |
| 7 | **Narrative Potential** | Can you tell a story that makes a skeptical reader care? |

## Persistent Evaluations

Evaluation results are **saved to disk** so they persist across sessions:

- After each session, verdicts are written to `research-evaluations/YYYY-MM-DD-<topic>.md`
- On subsequent sessions, the system **checks for prior evaluations** of similar topics before starting fresh
- PARK'd ideas include "revisit conditions" — what would need to change to reconsider
- The Research Strategist outputs a **watch list** for competitive tracking

## Differences from the Claude Code Version

| Feature | Claude Code Plugin | Copilot Adaptation |
|---------|-------------------|-------------------|
| Agent dispatch | Sub-agents with `subagent_type` | Role instructions in `agents/*.md` referenced by Copilot |
| Skill triggers | `/research-companion` slash command | Natural language requests |
| Plugin metadata | `.claude-plugin/`, `marketplace.json` | `.github/copilot-instructions.md` |
| Persistent state | `~/.claude/projects/*/memory/` | `research-evaluations/` in project dir |
| Model selection | Frontmatter `model: opus` | Uses whatever model Copilot is configured with |

## Philosophy

Most researchers optimize for publication count. The best researchers optimize for impact — and papers follow naturally. This project is built around that distinction.

It won't help you produce more papers. It will help you produce *better* ones by being honest about which ideas are worth your finite time.

The agents are deliberately opinionated and direct. They'd rather save you 3 months than spare your feelings.

## Credits

Original concept and content by [Andre Huang](https://github.com/andrehuang) ([research-companion](https://github.com/andrehuang/research-companion)), licensed under MIT. Adapted for GitHub Copilot.

## License

MIT
