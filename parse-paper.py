#!/usr/bin/env python3
"""Parse a single arXiv paper XML file and print details."""
import sys
import xml.etree.ElementTree as ET

with open(sys.argv[1]) as f:
    data = f.read()

if not data.strip():
    print("No response from arXiv API.")
    sys.exit(1)

root = ET.fromstring(data)
ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

entry = root.find("atom:entry", ns)
if entry is None:
    print("Paper not found.")
    sys.exit(1)

title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
summary = entry.find("atom:summary", ns).text.strip()
arxiv_id = entry.find("atom:id", ns).text.strip().split("/")[-1]
published = entry.find("atom:published", ns).text[:10]
updated = entry.find("atom:updated", ns).text[:10]

categories = [cat.get("term") for cat in entry.findall("atom:category", ns)]
authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]

pdf_link = ""
for link in entry.findall("atom:link", ns):
    if link.get("title") == "pdf":
        pdf_link = link.get("href")

print(f"# {title}")
print()
print(f"- **arXiv ID**: {arxiv_id}")
print(f"- **Published**: {published} | Updated: {updated}")
print(f"- **Categories**: {', '.join(categories)}")
print(f"- **Authors**: {', '.join(authors)}")
print(f"- **URL**: https://arxiv.org/abs/{arxiv_id}")
if pdf_link:
    print(f"- **PDF**: {pdf_link}")
print()
print("## Abstract")
print()
print(summary)
