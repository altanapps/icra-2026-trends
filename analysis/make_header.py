#!/usr/bin/env python3
"""Render analysis/header.png — topic-share chart for the article header."""
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = Path(__file__).parent
papers = json.load(open(DIR.parent / "papers.json"))
N = len(papers)
kwd = dict(json.load(open(DIR / "stats.json"))["top_keywords"])
humanoid = sum(
    1 for p in papers
    if re.search(r"humanoid", p["title"] + " " + " ".join(p["keywords"]) + " " + p["abstract"][:200], re.I)
)

rows = sorted([
    ("Visual perception (deep learning)", kwd["Deep Learning for Visual Perception"]),
    ("Reinforcement learning", kwd["Reinforcement Learning"]),
    ("Motion & path planning", kwd["Motion and Path Planning"]),
    ("Imitation learning", kwd["Imitation Learning"]),
    ("Localization", kwd["Localization"]),
    ("SLAM", kwd["SLAM"]),
    ("Multi-robot systems", kwd["Multi-Robot Systems"]),
    ("Medical robots & systems", kwd["Medical Robots and Systems"]),
    ("Legged robots", kwd["Legged Robots"]),
    ("Humanoids", humanoid),
], key=lambda r: r[1])

RED, GRAY, DARK = "#CF233A", "#9aa0a6", "#1a1a1a"
fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
fig.patch.set_facecolor("white")

labels = [r[0] for r in rows]
vals = [r[1] / N * 100 for r in rows]
bars = ax.barh(labels, vals, color=[RED if l == "Humanoids" else GRAY for l in labels], height=0.62)

for bar, name, v in zip(bars, labels, vals):
    bold = "bold" if name == "Humanoids" else "normal"
    col = RED if name == "Humanoids" else DARK
    ax.text(v + 0.12, bar.get_y() + bar.get_height() / 2, f"{v:.1f}%",
            va="center", fontsize=15, fontweight=bold, color=col, family="Georgia")

hum_y = labels.index("Humanoids")
ax.annotate("where the money is", xy=(vals[hum_y] + 0.55, hum_y), xytext=(vals[hum_y] + 2.4, hum_y),
            va="center", fontsize=16, style="italic", color=RED, family="Georgia",
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.8))

ax.set_title("ICRA 2026, all 2,951 papers: share by topic",
             fontsize=26, family="Georgia", fontweight="bold", color=DARK, loc="left", pad=24)
ax.text(0, 1.015, "Robotics' biggest conference, Vienna, June 2026 · source: official program, ras.papercept.net",
        transform=ax.transAxes, fontsize=13.5, color="#777", family="Georgia")

ax.set_xlim(0, max(vals) * 1.22)
ax.tick_params(axis="y", labelsize=16, length=0)
ax.tick_params(axis="x", labelsize=12, colors="#999")
for lbl in ax.get_yticklabels():
    lbl.set_family("Georgia")
    if lbl.get_text() == "Humanoids":
        lbl.set_color(RED)
        lbl.set_fontweight("bold")
    else:
        lbl.set_color(DARK)
ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0f}%")
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#ddd")
ax.set_axisbelow(True)
ax.grid(axis="x", color="#eee")

plt.tight_layout(pad=2.2)
plt.savefig(DIR / "header.png", bbox_inches="tight", facecolor="white")
print("saved analysis/header.png")
