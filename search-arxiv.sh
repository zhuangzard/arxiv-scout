#!/bin/bash
# 搜索arXiv论文
# 用法: search-arxiv.sh "query" [max_results] [category]
# 例: search-arxiv.sh "robot reasoning" 10 cs.RO

QUERY="${1:-robot reasoning}"
MAX="${2:-10}"
CAT="${3:-}"

if [ -n "$CAT" ]; then
    SEARCH="(cat:${CAT}) AND (all:${QUERY})"
else
    SEARCH="all:${QUERY}"
fi

# Fetch to temp file, then parse
TMPFILE=$(mktemp)
curl -sL -G "https://export.arxiv.org/api/query" \
    --data-urlencode "search_query=${SEARCH}" \
    -d "start=0" \
    -d "max_results=${MAX}" \
    -d "sortBy=submittedDate" \
    -d "sortOrder=descending" \
    -o "$TMPFILE"

python3 -c '
import sys
import xml.etree.ElementTree as ET

with open(sys.argv[1]) as f:
    data = f.read()

if not data.strip():
    print("No response from arXiv API.")
    sys.exit(1)

root = ET.fromstring(data)
ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

entries = root.findall("atom:entry", ns)
if not entries:
    print("No results found.")
    sys.exit(0)

for i, entry in enumerate(entries, 1):
    title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
    summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")[:200]
    arxiv_id = entry.find("atom:id", ns).text.strip().split("/")[-1]
    published = entry.find("atom:published", ns).text[:10]

    categories = []
    for cat in entry.findall("atom:category", ns):
        categories.append(cat.get("term"))
    cats_str = ", ".join(categories[:3])

    authors = []
    for author in entry.findall("atom:author", ns):
        name = author.find("atom:name", ns).text
        authors.append(name)
    authors_str = ", ".join(authors[:3])
    if len(authors) > 3:
        authors_str += f" +{len(authors)-3}"

    print(f"--- [{i}] {arxiv_id} ({published}) ---")
    print(f"Title: {title}")
    print(f"Authors: {authors_str}")
    print(f"Categories: {cats_str}")
    print(f"Abstract: {summary}...")
    print(f"URL: https://arxiv.org/abs/{arxiv_id}")
    print()
' "$TMPFILE"

rm -f "$TMPFILE"
