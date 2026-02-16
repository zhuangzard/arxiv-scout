#!/bin/bash
# 获取单篇论文详细信息
# 用法: fetch-paper.sh <arxiv_id>
# 例: fetch-paper.sh 2602.07885

ID="${1}"
if [ -z "$ID" ]; then
    echo "Usage: fetch-paper.sh <arxiv_id>"
    exit 1
fi

TMPFILE=$(mktemp)
curl -sL "https://export.arxiv.org/api/query?id_list=${ID}" -o "$TMPFILE"

python3 "$( cd "$( dirname "$0" )" && pwd )/parse-paper.py" "$TMPFILE"

rm -f "$TMPFILE"
