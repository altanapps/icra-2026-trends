export const meta = {
  name: 'icra-2026-trends',
  description: 'Extract trends from all 2,951 ICRA 2026 papers and synthesize a trends brief',
  phases: [
    { title: 'Extract', detail: '30 agents, ~98 papers each' },
    { title: 'Synthesize', detail: 'merge reports + stats into trends-brief.md' },
  ],
}

const DIR = '/Users/altan/Desktop/main/icra-2026-vienna-papers/analysis'

const BATCH_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['themes', 'methods_shift', 'notable', 'industry_signal', 'contrarian', 'humanoid'],
  properties: {
    themes: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'whats_new', 'share', 'exemplars'],
        properties: {
          name: { type: 'string' },
          whats_new: { type: 'string' },
          share: { type: 'string' },
          exemplars: { type: 'array', items: { type: 'string' } },
        },
      },
    },
    methods_shift: { type: 'string' },
    notable: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'why'],
        properties: { id: { type: 'string' }, why: { type: 'string' } },
      },
    },
    industry_signal: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'company', 'what_theyre_building'],
        properties: {
          id: { type: 'string' },
          company: { type: 'string' },
          what_theyre_building: { type: 'string' },
        },
      },
    },
    contrarian: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'finding'],
        properties: { id: { type: 'string' }, finding: { type: 'string' } },
      },
    },
    humanoid: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'signal'],
        properties: { id: { type: 'string' }, signal: { type: 'string' } },
      },
    },
  },
}

phase('Extract')
const nums = Array.from({ length: 30 }, (_, i) => String(i + 1).padStart(2, '0'))
const reports = await parallel(nums.map(n => () =>
  agent(
    `Read the file ${DIR}/batches/batch_${n}.txt. It contains a trend-spotting task and ~98 ICRA 2026 robotics papers (id, title, session, keywords, abstract). Follow its instructions exactly and return your findings as structured output. Be concrete — cite paper ids, name actual techniques, and leave lists empty rather than padding.`,
    { label: `extract:batch_${n}`, phase: 'Extract', schema: BATCH_SCHEMA }
  ).then(r => r ? { batch: n, ...r } : null)
))
const good = reports.filter(Boolean)
log(`${good.length}/30 batch reports completed`)

phase('Synthesize')
const reportsJson = JSON.stringify(good)
const summary = await agent(
  `You are synthesizing a trend analysis of ICRA 2026 (Vienna, June 1-5, 2026) — all 2,951 accepted papers.

You have two inputs:
A. DATASET STATS — exact counts over all 2,951 papers. Read them from ${DIR}/stats.json. These are ground truth.
B. BATCH REPORTS — trend extractions from ${good.length} agents who each read ~98 full abstracts, included below. These are observations; they may disagree with each other.

First, save the batch reports verbatim: Write the JSON below, exactly as given, to ${DIR}/batch-reports.json.

Then Write a trends brief to ${DIR}/trends-brief.md, in markdown, for a technical founder writing a public essay:

# ICRA 2026: What 2,951 Papers Say About Where Robotics Is Going

## Macro trends — the 5-7 macro trends. Each as: ### heading with a one-sentence claim, then evidence (counts from A + exemplar papers cited by title and id from B), then "What changed:" versus the previous consensus in robotics.
## The tensions — where the field visibly disagrees (learning vs model-based, sim vs real data, end-to-end vs modular...).
## The white space — what's conspicuously rare given the hype.
## Industry watch — which companies published what, and what that reveals about their roadmaps.
## Humanoid deep-dive — the 2026 state-of-the-art recipe for making a humanoid walk, as evidenced by these papers.

Rules:
- Every claim needs either a count from A or >=2 named papers from B.
- Quantify ("X of 2,951") wherever stats allow.
- Where batch reports disagree, flag the disagreement — don't average it away.
- No filler trends. If only 5 are real, write 5.
- Exemplar papers: cite by full title plus paper id. Look up titles in ${DIR}/../papers.json (grep by paper id) when a batch report only gives an id.

When both files are written, return a 10-line plain-text summary: the macro-trend claims (one line each) plus anything that surprised you.

=== B. BATCH REPORTS (JSON) ===
${reportsJson}`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return { batches_completed: good.length, summary }