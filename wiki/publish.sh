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

# Author identity for the wiki commit. Defaults to a GitHub no-reply address so
# the push is never rejected by GitHub's email-privacy protection (error GH007,
# "your push would publish a private email address"). Override with the
# environment variables if you publish under a different account.
WIKI_AUTHOR_NAME="${WIKI_AUTHOR_NAME:-Arnav}"
WIKI_AUTHOR_EMAIL="${WIKI_AUTHOR_EMAIL:-951585+arnavj@users.noreply.github.com}"

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

# Commit with an explicit, hide-able identity so the run doesn't depend on the
# machine's git config and can't trip GitHub's email-privacy push protection.
git -c user.name="$WIKI_AUTHOR_NAME" -c user.email="$WIKI_AUTHOR_EMAIL" \
    commit -F - <<'MSG'
Update wiki from main repo wiki/ sources

Co-Authored-By: Claude <noreply@anthropic.com>
MSG
echo "🚀 Pushing to the wiki…"
git push
echo "✅ Published: https://github.com/arnavj/SlopeScript/wiki"
