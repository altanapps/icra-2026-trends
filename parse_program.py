#!/usr/bin/env python3
"""Parse ICRA 2026 PaperCept program pages (raw/day_*.html) into papers.json / papers.csv."""
import csv
import html
import json
import re
from pathlib import Path

RAW = Path(__file__).parent / "raw"
OUT = Path(__file__).parent

DAYS = {
    "day_3.html": "Tuesday June 2, 2026",
    "day_4.html": "Wednesday June 3, 2026",
    "day_5.html": "Thursday June 4, 2026",
}

TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(s: str) -> str:
    return html.unescape(TAG_RE.sub("", s)).strip()


def parse_day(path: Path, day: str):
    data = path.read_text(encoding="windows-1252")
    papers = []

    # Split the document at each paper header; session headers appear between them.
    # Track the current session by scanning sHdr rows as we move through the file.
    session_re = re.compile(
        r'<tr class="sHdr">\s*<td nowrap><a name="[^"]*"><b>([A-Za-z0-9]+)</b>(.*?)</td>',
        re.S,
    )
    paper_re = re.compile(
        r'<tr class="pHdr"><td valign="bottom"><a name="[^"]*">([\d:>-]+|[^<]*?), Paper ([A-Za-z0-9.]+)</a>',
    )
    title_re = re.compile(r'<span class="pTtl">&nbsp;(?:<a [^>]*>)?(.*?)(?:</a>)?</span>', re.S)
    author_re = re.compile(
        r'<tr><td><a href="ICRA26_AuthorIndexWeb\.html#\d+"[^>]*>(.*?)</a></td><td class="r">(.*?)</td></tr>',
        re.S,
    )
    abstract_div_re = re.compile(r'<div id="Ab\d+"[^>]*>(.*?)</div>', re.S)
    keywords_re = re.compile(
        r'<a href="ICRA26_KeywordIndexWeb\.html#[^"]*"[^>]*>(.*?)</a>', re.S
    )
    abstract_re = re.compile(r"<strong>Abstract:</strong>(.*)", re.S)

    # Build an ordered list of (position, kind, payload) events
    events = []
    for m in session_re.finditer(data):
        code, rest = m.group(1), strip_tags(m.group(2))
        events.append((m.start(), "session", (code, rest.lstrip("\xa0 ").strip())))
    for m in paper_re.finditer(data):
        events.append((m.start(), "paper", (m.group(1), m.group(2), m.end())))
    events.sort(key=lambda e: e[0])

    session_code, session_title = "", ""
    paper_spans = [e for e in events if e[1] == "paper"]
    for idx, (pos, kind, payload) in enumerate(events):
        if kind == "session":
            session_code, session_title = payload
            continue
        time_slot, paper_code, end = payload
        # The paper's block runs until the next paper or session header
        nxt = next((e[0] for e in events[idx + 1:]), len(data))
        block = data[end:nxt]

        tm = title_re.search(block)
        title = strip_tags(tm.group(1)) if tm else ""

        authors = [
            (strip_tags(n), strip_tags(a)) for n, a in author_re.findall(block)
        ]

        keywords, abstract = [], ""
        am = abstract_div_re.search(block)
        if am:
            ab_block = am.group(1)
            keywords = [strip_tags(k) for k in keywords_re.findall(ab_block)]
            keywords = [k for k in keywords if k]
            xm = abstract_re.search(ab_block)
            if xm:
                abstract = strip_tags(xm.group(1))

        papers.append(
            {
                "paper_id": paper_code,
                "day": day,
                "time": time_slot.strip(),
                "session_code": session_code,
                "session": session_title,
                "title": title,
                "authors": [n for n, _ in authors],
                "affiliations": sorted({a for _, a in authors if a}),
                "author_affiliations": [
                    {"name": n, "affiliation": a} for n, a in authors
                ],
                "keywords": keywords,
                "abstract": abstract,
            }
        )
    return papers


def main():
    all_papers = []
    for fname, day in DAYS.items():
        papers = parse_day(RAW / fname, day)
        print(f"{day}: {len(papers)} papers")
        all_papers.extend(papers)

    print(f"Total: {len(all_papers)} papers")
    missing_title = [p for p in all_papers if not p["title"]]
    missing_abs = [p for p in all_papers if not p["abstract"]]
    print(f"Missing title: {len(missing_title)}, missing abstract: {len(missing_abs)}")

    (OUT / "papers.json").write_text(
        json.dumps(all_papers, indent=1, ensure_ascii=False), encoding="utf-8"
    )

    with open(OUT / "papers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["paper_id", "day", "time", "session", "title", "authors", "affiliations", "keywords", "abstract"]
        )
        for p in all_papers:
            w.writerow(
                [
                    p["paper_id"],
                    p["day"],
                    p["time"],
                    p["session"],
                    p["title"],
                    "; ".join(p["authors"]),
                    "; ".join(p["affiliations"]),
                    "; ".join(p["keywords"]),
                    p["abstract"],
                ]
            )


if __name__ == "__main__":
    main()
