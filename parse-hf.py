#!/usr/bin/env python3
"""Parse HuggingFace daily papers JSON."""
import json
import sys

with open(sys.argv[1]) as f:
    papers = json.load(f)

for i, p in enumerate(papers, 1):
    paper = p["paper"]
    upvotes = p.get("numUpvotes", 0)
    arxiv_id = paper["id"]
    title = paper["title"][:100]
    summary = paper.get("summary", "")[:200]
    authors = [a["name"] for a in paper.get("authors", [])[:3]]
    authors_str = ", ".join(authors)
    if len(paper.get("authors", [])) > 3:
        authors_str += f' +{len(paper["authors"])-3}'

    print(f"--- [{i}] ⬆️{upvotes} | {arxiv_id} ---")
    print(f"Title: {title}")
    print(f"Authors: {authors_str}")
    print(f"Abstract: {summary}...")
    print(f"URL: https://arxiv.org/abs/{arxiv_id}")
    print()
