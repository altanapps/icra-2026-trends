#!/usr/bin/env python3
"""Render a markdown file to .html + .pdf (via headless Chrome). Usage: make_pdf.py [file.md]"""
import html as H
import re
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).parent
md = (Path(sys.argv[1]) if len(sys.argv) > 1 else DIR / "trends-brief.md").resolve()
src = md.read_text()


def inline(s):
    s = H.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


out, in_list = [], False
for line in src.split("\n"):
    t = line.strip()
    if in_list and not t.startswith("- "):
        out.append("</ul>")
        in_list = False
    if not t:
        continue
    if t == "---":
        out.append("<hr>")
    elif t.startswith("### "):
        out.append(f"<h3>{inline(t[4:])}</h3>")
    elif t.startswith("## "):
        out.append(f"<h2>{inline(t[3:])}</h2>")
    elif t.startswith("# "):
        out.append(f"<h1>{inline(t[2:])}</h1>")
    elif t.startswith("- "):
        if not in_list:
            out.append("<ul>")
            in_list = True
        out.append(f"<li>{inline(t[2:])}</li>")
    else:
        out.append(f"<p>{inline(t)}</p>")
if in_list:
    out.append("</ul>")

doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@page {{ margin: 22mm 19mm; }}
body {{ font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.55; color: #1a1a1a; }}
h1 {{ font-size: 19pt; line-height: 1.25; border-bottom: 2px solid #CF233A; padding-bottom: 8px; }}
h2 {{ font-size: 14pt; margin-top: 26px; color: #CF233A; }}
h3 {{ font-size: 11.5pt; margin-top: 18px; }}
code {{ font-family: Menlo, monospace; font-size: 9pt; background: #f4f4f4; padding: 1px 3px; }}
hr {{ border: none; border-top: 1px solid #ccc; margin: 22px 0; }}
li {{ margin-bottom: 6px; }}
p {{ margin: 8px 0; text-align: justify; }}
</style></head><body>
{chr(10).join(out)}
<p style="color:#888; font-size:8.5pt; margin-top:30px;">Generated 11 June 2026 from the official ICRA 2026 program (ras.papercept.net) — 2,951 program entries, 30 independent full-abstract readings + exact corpus statistics.</p>
</body></html>"""
out_html = md.with_suffix(".html")
out_pdf = md.with_suffix(".pdf")
out_html.write_text(doc)

subprocess.run(
    [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={out_pdf}",
        f"file://{out_html}",
    ],
    check=True,
    capture_output=True,
)
print(f"Wrote {out_html.name} and {out_pdf.name}")
