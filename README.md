# ICRA 2026 — Papers Dataset & Trend Analysis

All **2,951 papers** from the ICRA 2026 technical program (Vienna, Austria, June 1–5, 2026),
extracted from the official PaperCept program and analyzed for field-wide trends.

Scraped 2026-06-11 from https://ras.papercept.net/conferences/conferences/ICRA26/program/
(program last updated June 8, 2026).

**What "2,951 papers" means:** every entry in the technical program (Tue June 2 – Thu June 4) —
peer-reviewed contributed papers, journal papers (RA-L and similar) presented at the conference,
131 late-breaking results, and 36 award-session entries. This is *presented at ICRA 2026*, not
*accepted by ICRA* (the official acceptance count is not yet published; the conference received
5,088 submissions). 2,761 entries include full abstracts.

## The headline outputs

| File | What |
|---|---|
| [`analysis/trends-brief.md`](analysis/trends-brief.md) | The full trend analysis — 6 macro trends, tensions, white space, industry watch, humanoid deep-dive — every claim backed by exact counts or named papers |
| [`analysis/x-article.md`](analysis/x-article.md) | Short-form essay version of the same analysis |
| [`papers.json`](papers.json) | All 2,951 papers — id, day, time, session, title, authors, affiliations, keywords, abstract |
| [`papers.csv`](papers.csv) | Same data flattened for spreadsheets |

## How the analysis was produced

1. **Scrape & parse** — `parse_program.py` parses the official program HTML (`raw/day_*.html`)
   into `papers.json` / `papers.csv`.
2. **Exact stats** — `build_analysis.py` computes keyword frequencies, keyword co-occurrence,
   and company-vs-university affiliation counts over the full corpus (`analysis/stats.json`),
   and assembles 30 batch prompts of ~98 papers each, randomly assigned with a fixed seed
   (`analysis/batches/`).
3. **Parallel extraction** — 30 independent LLM agents each read one batch (full abstracts) and
   return structured findings: themes, method shifts, notable papers, industry signals,
   contrarian results, humanoid signals. Prompts in `analysis/analysis-prompts.md`; orchestration
   in `analysis/workflow.js` (Claude Code workflow); raw outputs in `analysis/batch-reports.json`.
4. **Synthesis** — one agent merges all 30 reports against the exact stats (ground truth for any
   quantitative claim) into `analysis/trends-brief.md`. Disagreements between batch readings are
   flagged, not averaged away.
5. **Verification** — every numeric claim in the essay version was checked against the source
   abstracts in `papers.json`.

## Replicating

```bash
# 1. Re-download the program and rebuild the dataset
#    (pages: ICRA26_ContentListWeb_3..5.html -> raw/day_3..5.html)
python3 parse_program.py

# 2. Rebuild stats + batch prompts (deterministic, seed=26)
python3 build_analysis.py

# 3. Run the 30 extraction prompts in analysis/batches/ through the LLM of your
#    choice with the JSON schema in analysis/analysis-prompts.md, then synthesize
#    with the Stage 2 prompt. analysis/workflow.js is the Claude Code version.

# Render any markdown output to PDF (requires Chrome)
python3 analysis/make_pdf.py analysis/trends-brief.md
```

## Notes

- Paper PDFs are **not** included — full texts are behind IEEE Xplore. Abstracts here are from
  the public program. `paper_id` (e.g. `TuI1I.101`) is the official PaperCept session.paper code.
- The company-affiliation detector (`build_analysis.py`) is regex-based and conservative;
  expect small undercounts, not overcounts.
- Top keywords: Deep Learning for Visual Perception (253), Reinforcement Learning (250),
  Motion and Path Planning (229), Imitation Learning (196), Localization (163).
