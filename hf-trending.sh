#!/bin/bash
# 获取HuggingFace今日热门论文
# 用法: hf-trending.sh [limit]

LIMIT="${1:-30}"
TMPFILE=$(mktemp)

curl -sL "https://huggingface.co/api/daily_papers?limit=${LIMIT}" -o "$TMPFILE"

python3 "$( cd "$( dirname "$0" )" && pwd )/parse-hf.py" "$TMPFILE"

rm -f "$TMPFILE"
