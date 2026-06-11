#!/usr/bin/env python3
"""Build analysis inputs from papers.json: exact corpus stats + 30 batch prompts.

Stage 0 of the trend analysis (see analysis/analysis-prompts.md for the full
methodology). Outputs analysis/stats.json and analysis/batches/batch_NN.txt.
"""
import collections
import json
import os
import random
import re
from pathlib import Path

DIR = Path(__file__).parent
papers = json.load(open(DIR / "papers.json"))

# --- Exact corpus statistics ---
kw = collections.Counter()
cooc = collections.Counter()
for p in papers:
    ks = p["keywords"]
    for k in ks:
        kw[k] += 1
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            cooc[tuple(sorted((ks[i], ks[j])))] += 1

COMPANY_PAT = re.compile(
    r"\b(GmbH|Inc\b|Ltd|LLC|Corp\b|AG$|NVIDIA|Google|DeepMind|Amazon|Meta\b|Apple"
    r"|Huawei|Samsung|Sony|Toyota|Honda|Hyundai|Bosch|Siemens|ABB|KUKA"
    r"|Boston Dynamics|Agility Robotics|Unitree|ANYbotics|Franka|Intrinsic|Dyson"
    r"|Naver|Tencent|Alibaba|ByteDance|Xiaomi|Horizon Robotics|Skild"
    r"|Physical Intelligence|Toyota Research Institute|Microsoft|Qualcomm"
    r"|Mitsubishi|Panasonic|Disney Research|Dexterity|Covariant|Wayve|Waymo"
    r"|Zoox|Nuro|DJI)",
    re.I,
)
UNI_PAT = re.compile(
    r"(Universit|Institute of Technology|ETH|EPFL|KAIST|MIT\b|Carnegie|College"
    r"|Politecnico|TU\b|KTH|CNRS|INRIA|Max Planck|Academy of Sciences|School"
    r"|Caltech|Tech$|SUSTech|POSTECH|DLR|Fraunhofer|National Laboratory)",
    re.I,
)

company_papers, comp_count = [], collections.Counter()
for p in papers:
    comps = [a for a in p["affiliations"] if COMPANY_PAT.search(a) and not UNI_PAT.search(a)]
    if comps:
        company_papers.append(p["paper_id"])
        for c in comps:
            comp_count[c] += 1

# Method mentions: papers whose title or abstract matches each pattern.
# The PaperCept keyword taxonomy has no tags for these, so we count directly.
METHOD_PATTERNS = {
    "diffusion (any mention)": r"\bdiffusion\b",
    "diffusion policy": r"diffusion[- ]based polic|diffusion polic",
    "flow matching": r"flow[- ]matching|flow matching",
    "VLA / vision-language-action": r"vision[- ]language[- ]action|\bVLA\b",
    "LLM / large language model": r"\bLLMs?\b|large language model",
    "model predictive control": r"model[- ]predictive|\bMPC\b",
    "control barrier function": r"control barrier|CBF",
    "teleoperation": r"teleoperat",
    "human video / egocentric": r"human video|egocentric",
    "imitation learning (text mention)": r"imitation learning",
    "gaussian splatting": r"gaussian splat|3DGS",
    "NeRF / neural radiance": r"NeRF|neural radiance",
}
method_mentions = {
    name: sum(1 for p in papers if re.search(pat, p["title"] + " " + p["abstract"], re.I))
    for name, pat in METHOD_PATTERNS.items()
}

os.makedirs(DIR / "analysis", exist_ok=True)
stats = {
    "total_papers": len(papers),
    "papers_with_company_affiliation": len(company_papers),
    "top_keywords": kw.most_common(40),
    "top_keyword_pairs": [[f"{a} + {b}", c] for (a, b), c in cooc.most_common(25)],
    "top_companies": comp_count.most_common(30),
    "method_mentions": method_mentions,
}
json.dump(stats, open(DIR / "analysis" / "stats.json", "w"), indent=1, ensure_ascii=False)

# --- Batch prompts: 30 random batches, full abstracts ---
N_BATCHES = 30
random.seed(26)  # fixed seed -> reproducible batch assignment
shuffled = papers[:]
random.shuffle(shuffled)
batches = [shuffled[i::N_BATCHES] for i in range(N_BATCHES)]

HEADER = """You are analyzing batch {i} of {n_batches} from ICRA 2026 (Vienna, June 2026), the premier
robotics conference. Below are {n} papers, randomly sampled from the full set of 2,951.
For each: id, title, session, keywords, abstract.

Your job is trend-spotting, not summarization. Return JSON with:

1. "themes": 3-6 dominant technical themes in this batch. Each: {{name, whats_new
   (what's actually new vs standard practice), share (rough fraction of batch),
   exemplars (2-3 paper ids)}}.
2. "methods_shift": which methods appear as the DEFAULT tool (diffusion policies,
   VLAs, RL-in-sim, classical MPC...) and what seems to be displacing what.
   Plain text, name actual techniques.
3. "notable": up to 5 individually striking papers — a result that would surprise
   a robotics-literate reader, an unusually strong claim, a first-of-its-kind.
   Each: {{id, why (one sentence)}}.
4. "industry_signal": papers from companies rather than universities —
   {{id, company, what_theyre_building}}. Empty list if none; do not stretch.
5. "contrarian": papers cutting AGAINST the mainstream narrative — classical
   methods beating learning, negative results, sim2real failures. Each: {{id, finding}}.
6. "humanoid": signals specific to humanoid/legged platforms — hardware, actuators,
   locomotion recipes, cost. Each: {{id, signal}}.

Be concrete: name actual techniques and cite paper ids. Don't pad — empty lists
are valid answers.

PAPERS:

"""


def paper_block(p):
    ab = p["abstract"] or "(no abstract in program)"
    return (
        f"[{p['paper_id']}] {p['title']}\n"
        f"Session: {p['session']} | Keywords: {'; '.join(p['keywords']) or '-'}\n"
        f"Affiliations: {'; '.join(p['affiliations'])}\n"
        f"Abstract: {ab}\n"
    )


os.makedirs(DIR / "analysis" / "batches", exist_ok=True)
for i, b in enumerate(batches, 1):
    txt = HEADER.format(i=i, n_batches=N_BATCHES, n=len(b)) + "\n".join(
        paper_block(p) for p in b
    )
    (DIR / "analysis" / "batches" / f"batch_{i:02d}.txt").write_text(txt)

print(f"Wrote analysis/stats.json and {N_BATCHES} batch prompts")
print(f"Total: {len(papers)} papers, {len(company_papers)} with company affiliation")
