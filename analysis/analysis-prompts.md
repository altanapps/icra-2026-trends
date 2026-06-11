# ICRA 2026 Trend Analysis — Prompt Design

Goal: extract writable trends across all 2,951 ICRA 2026 papers (titles, sessions,
keywords, abstracts — not full texts) for a public essay.

## Architecture

- **Stage 0 — stats (pure Python, no LLM):** keyword frequencies, session-topic
  distribution, company-vs-university affiliation counts, keyword co-occurrence.
  Grounds every qualitative claim in an exact count.
- **Stage 1 — ~30 parallel batch agents, ~100 papers each,** randomly assigned
  (not by session, to avoid single-topic batches). Full abstracts, structured
  JSON output.
- **Stage 2 — one synthesis agent:** all 30 batch reports + Stage 0 stats.
- **Stage 3 (optional) — fact-check agent:** verify the brief's top claims
  against papers.json before anything goes public.

## Stage 1 prompt (per batch)

You are analyzing batch {i} of 30 from ICRA 2026 (Vienna, June 2026) — {n}
papers, each with id, title, session, keywords, abstract. Your job is
trend-spotting, not summarization. Return:

1. themes — 3–6 dominant technical themes in this batch. For each: a name,
   what's actually new versus standard practice, rough share of the batch,
   2–3 exemplar paper ids.
2. methods_shift — which methods appear as the default tool (diffusion
   policies, VLAs, RL-in-sim, classical MPC…) and what seems to be displacing
   what.
3. notable — up to 5 individually striking papers: a result that would
   surprise a robotics-literate reader, an unusually strong claim, a
   first-of-its-kind. One sentence each on why.
4. industry_signal — papers from companies rather than universities, and what
   they're working on.
5. contrarian — anything cutting against the mainstream narrative: classical
   methods beating learning, negative results, sim2real failures.
6. humanoid — any signal specific to humanoid/legged platforms: hardware,
   actuators, locomotion recipes, cost.

Be concrete: name actual techniques and cite paper ids. Don't pad — if this
batch has no industry papers, say so.

## Stage 2 prompt (synthesis)

You have trend extractions from 30 batches covering all 2,951 ICRA 2026
papers, plus exact dataset-wide statistics. Produce a trends brief for a
technical founder writing a public essay:

1. The 5–7 macro trends — each as: one-sentence claim, evidence (counts from
   the stats + exemplar papers by title), and what changed versus the previous
   consensus.
2. The tensions — where the field visibly disagrees (learning vs model-based,
   sim vs real data…).
3. The white space — what's conspicuously rare given the hype.
4. Industry watch — which companies published, and what that reveals about
   roadmaps.
5. Humanoid deep-dive — the 2026 state-of-the-art recipe for making a humanoid
   walk, as evidenced by these papers.

Rules: every claim needs either a count or ≥2 named papers behind it.
Quantify ("X of 2,951") wherever the stats allow. Where batch reports
disagree, flag the disagreement — don't average it away.

## Cost estimate

~30 agents × ~35k tokens in / ~2k out + synthesis ≈ 1–1.5M input tokens,
a few minutes wall-clock as a multi-agent workflow.
