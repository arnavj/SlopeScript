#!/usr/bin/env bash
#
# publish.sh — publish wiki/*.md to the SlopeScript GitHub wiki.
#
# GitHub wikis are a separate git repository (SlopeScript.wiki.git). This
# script copies the reviewed Markdown sources in this directory into that
# repo and pushes them.
#
# One-time setup: the wiki must have at least one page before its git repo
# exists. Visit https://github.com/arnavj/SlopeScript/wiki and click
# "Create the first page" (save anything — it gets overwritten below).
#
# Usage (from anywhere):
#   ./wiki/publish.sh
#
set -euo pipefail

WIKI_REMOTE="https://github.com/arnavj/SlopeScript.wiki.git"

# Directory this script lives in (the wiki/ source dir).
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

WORK_DIR="$(mktemp -d)"
cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT

echo "🎿 Cloning the wiki repo…"
if ! git clone "$WIKI_REMOTE" "$WORK_DIR/wiki" 2>/dev/null; then
  echo "❌ Could not clone $WIKI_REMOTE"
  echo "   Initialise the wiki first: open"
  echo "   https://github.com/arnavj/SlopeScript/wiki and create the first page."
  exit 1
fi

echo "📄 Copying Markdown pages…"
cp "$SRC_DIR"/*.md "$WORK_DIR/wiki/"
# The wiki source README documents this directory; it isn't a wiki page.
rm -f "$WORK_DIR/wiki/README.md"

cd "$WORK_DIR/wiki"
git add -A

if git diff --cached --quiet; then
  echo "✅ Wiki already up to date — nothing to publish."
  exit 0
fi

git commit -m "Update wiki from main repo wiki/ sources"
echo "🚀 Pushing to the wiki…"
git push
echo "✅ Published: https://github.com/arnavj/SlopeScript/wiki"
