# I analyzed all 2,951 papers from robotics' biggest conference. The field isn't going where the money is.

ICRA wrapped in Vienna last week. It's the conference where robotics shows its hand: 2,951 papers presented across three days, from every major lab and company in the field.

Inside those papers: NVIDIA's flagship GR00T falling from 90% to 4.5% when tasks go multi-step. Humanoids, widely reported as the most-funded category in robotics, at 3.5% of the research. A model that hallucinates force signals from vision beating the physical force sensor it was trained to imitate.

I extracted every paper from the official technical program ([ras.papercept.net](https://ras.papercept.net/conferences/conferences/ICRA26/program/)) and ran a structured analysis across all of them: every abstract read, plus exact keyword and affiliation counts over the full corpus. The dataset and every line of code are public, so you can check anything I say here. Not vibes. Counts.

Six things stood out.

## 1. Diffusion policies won, and the field has already moved on to fixing them

Two years ago the debate was diffusion policy vs. ACT vs. plain behavior cloning. That debate is over. Nobody at ICRA 2026 is asking whether generative action policies work. They're the assumed default, and the papers are about patching them: one hits 95% of state-of-the-art performance at 5% of the training time, another matches diffusion planners with ~100x faster inference, and flow matching is visibly eating diffusion from below.

When a method stops being the headline and becomes the infrastructure everyone else patches, it won.

## 2. LLMs got demoted, from robot brain to robot component

The 2023 dream was that one big model would absorb the whole robot, end to end. The 2026 reality, consistent across every slice of the conference: foundation models handle the semantics, and classical machinery keeps the guarantees. The LLM proposes a plan; a symbolic planner or scene-graph verifier checks it before the robot moves. The model is in the loop, but firewalled.

And here's the part nobody tweets: the same conference published the sharpest evidence yet that VLAs are fragile. A single adversarially textured object cut state-of-the-art VLA success rates by 31–40%. Visual clutter alone cut up to 34%. NVIDIA's flagship GR00T fell from 90% to 4.5% when tasks went multi-step — measured by independent evaluators, not by NVIDIA. And it's not just exotic attacks: ordinary observation shift from a preceding skill drops OpenVLA by 54%, with no standard remedy working.

The field is standardizing on VLAs while proving they memorize more than they understand. If you're betting a company on generalist robot policies, hold both facts at once.

## 3. Data quality beat data scale

The default heading into this year was "collect more teleop demos and train bigger." The fast-growing 2026 recipe: don't pay for teleop if you can avoid it. Microsoft turned a million episodes of ordinary human hand video into robot training data with zero annotation. A CMU–Meta team trained dexterous manipulation from Aria smart-glasses recordings, no robot data at all. A Georgia Tech–NVIDIA team crowdsourced 7,500+ demos across 9 countries in 5 days using smartphones.

Meanwhile, brute-force scale took direct empirical hits. A 30,000-hour autonomous-driving study found the imitation scaling law holds in open-loop testing but breaks down exactly where it matters: in closed-loop driving. Another paper showed curating your dataset beats growing it. The moat isn't data volume anymore. It's data quality.

## 4. Gaussian splatting quietly took over robot perception

Two years ago, NeRF was the assumed future of how robots represent the world. It lost before it ever became infrastructure: too slow, too hard to edit. At ICRA 2026, Gaussian-splatting papers outnumber NeRF papers roughly four to one (83 vs 23), and NeRF mostly appears as the baseline being beaten. The new representation shows up everywhere: kilometer-scale SLAM, simulators rendering LiDAR at 600+ FPS, even policies running inside a 60 Hz Gaussian digital twin that the real robot mirrors.

You can tell it's settled because the papers are engineering papers now: pruning it for embedded compute, handling dynamic scenes, coupling it to physics. That's what a default looks like.

## 5. The classical-vs-learning war ended in a merger

Reinforcement learning is the #2 topic of the entire conference (250 papers). And yet: a racecar held stable above 160 mph with zero learning. A GPU reimplementation of a classical solver beat the standard tools by up to 700% on single-rigid-body MPC. A full-size humanoid walked in real time on plain model-predictive control, no policy network in sight. An MCTS planner beat learned planners over 500+ public-road miles, and a symbolic-planning stack beat a fine-tuned VLA 95% to 34%, at roughly 100x less training energy. Learning's retreat is sharpest in driving, where rule-based baselines keep beating learned planners under realistic traffic.

The fastest-growing recipe isn't either side winning. It's learning inside structure. RL corrects a model-based controller's output. Safety certificates get baked into training instead of bolted on at runtime. Learned components propose; classical control disposes.

## 6. Robots are finally learning to feel

Vision-only manipulation hit a wall, and the field said so out loud. 86 papers on force and tactile sensing. Purpose-built hardware to capture touch during human demonstrations. Gloves under $700. Tactile simulators running 4,096 parallel training environments on one consumer GPU.

My favorite result of the entire conference: a model that hallucinates force signals from vision outperformed the physical force sensor it was trained to imitate.

## What almost nobody is working on

The gaps say as much as the trends:

- **Security.** Out of 2,951 papers, the ones treating robots as attack surfaces number in the single digits, including an internet-wide scan showing deployed ROS 2 robots are fingerprintable and exploitable in default configurations. Robots are shipping; security research isn't.
- **Reproducibility.** One paper showed state-of-the-art LiDAR-inertial odometry results don't replicate run to run. Another ran 5,040 grasping trials across labs and watched algorithm rankings flip with lighting. Almost nobody checks whether their own numbers hold.
- **Energy and cost.** The papers that meter what anything costs in joules or dollars can be counted on one hand. In a field whose products have to pencil out.

And the stat I can't stop thinking about: **humanoids — widely reported as the most-funded category in robotics — got 3.5% of the papers.** The capital is concentrated exactly where the research is thinnest.

You could argue the most-funded labs simply publish least. Maybe. But when the field's biggest conference gives 3.5% of its attention to the category absorbing the most capital, one of those two numbers is mispriced.

Meanwhile medical robotics, at 111 papers, is *bigger* than humanoids, and quietly moving from perception toward closed-loop autonomous surgery. Almost nobody outside the field is talking about it.

## The humanoid recipe, since that's where the money is

For making a humanoid walk in 2026, the field has converged hard:

- **Buy the platform.** The Unitree G1 is the new default humanoid research platform.
- **Get the actuator model right.** That, not the simulator, is the sim2real bottleneck.
- **Retarget human motion and train massively parallel RL in simulation.** Obsess over retargeting quality, not reward engineering — the standout parkour result this year used five reward terms and no curriculum; it just fixed the data.
- **Fold model-based control back in** where it's stronger.
- **Engineer for falling, not just against it.** Falls are now a skill robots train, complete with controlled-fall styles from Disney.

The demos got genuinely absurd: a humanoid sustained up to 106 consecutive table-tennis shots against a human opponent. The walking problem is converging. Which means the real problem, useful work, is about to take its place.

## What the companies revealed

**NVIDIA** (24 papers, more than any other company) publishes both robot policies and — most tellingly — the synthetic-data and training infrastructure for everyone else's robots.

**Toyota** is hedging across the entire spectrum, from millisecond classical control to video-diffusion data generation, and publishing detailed field-test failure analyses.

**Huawei** is publishing across the whole embodied-AI surface (perception, manipulation, simulation, data), including backing a ~$14k open-source bimanual humanoid with City University of Hong Kong.

**A cluster of Chinese robotics companies** — Galbot, Midea, ByteDance, Alibaba, Fourier — is publishing the humanoid stack layer by layer: wrist and hand hardware, data-collection rigs, training recipes.

**Google DeepMind's** quiet flex: a navigation foundation policy trained on crowd-sourced teleop and YouTube video, already deployed on robot fleets in six cities across three continents.

**Meta and Microsoft** are positioning wearables and in-the-wild human video as the data-acquisition layer for robotics.

---

The meta-trend underneath all six: robotics is leaving its demo era. The exciting papers in 2026 aren't "look what's possible." They're about latency, fragility, verification, data supply chains, and what breaks at 99%. That's what a field sounds like right before it becomes an industry.

---

## Data & methodology

Everything above is checkable:

- **Source:** the official ICRA 2026 technical program, [ras.papercept.net](https://ras.papercept.net/conferences/conferences/ICRA26/program/), scraped June 11, 2026 (program last updated June 8, per the page footer). The 2,951 figure counts program entries: peer-reviewed papers (contributed and journal presentations), 131 late-breaking results, and 36 award-session entries. The official acceptance count isn't published yet, so "papers" here means "presented in Vienna," not "accepted by ICRA."
- **Method:** all keyword, affiliation, and co-occurrence counts are exact, computed directly over the full dataset. The qualitative trends come from 30 independent LLM passes, each reading 98–99 full abstracts and returning structured findings, then synthesized against the exact counts. Every named result in this article was verified against its source abstract.

**Replicate anything:** the dataset, the scraper, the analysis pipeline, the 30 batch prompts, the raw reports, and the full trends brief with per-claim paper IDs are all here:

### → **[github.com/altanapps/icra-2026-trends](https://github.com/altanapps/icra-2026-trends)**
