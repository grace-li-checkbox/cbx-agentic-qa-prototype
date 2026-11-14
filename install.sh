#!/bin/sh
set -eu

repo=$(cd "$(dirname "$0")" && pwd)
skill="$repo/.claude/skills/quality-assurance"
target="$HOME/.claude/skills/quality-assurance"

mkdir -p "$HOME/.claude/skills"
if [ -e "$target" ] && [ ! -L "$target" ]; then
  echo "$target exists and is not a link. Move it away, then run this again." >&2
  exit 1
fi
ln -sfn "$skill" "$target"
echo "Linked $target -> $skill"

npm install -g @playwright/cli@0.1.24
npx -y playwright@1.66.0-alpha-1794252756000 install chromium ffmpeg

echo
echo "Done. Before a run, set ROUTINE_QA_EMAIL and ROUTINE_QA_PASSWORD for your local stack."
echo "Then, in Claude Code: /quality-assurance run"
