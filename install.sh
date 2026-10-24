#!/usr/bin/env sh
# Install the /insta-* skills into Claude Code and the igos CLI.
#   sh install.sh            global  (~/.claude/skills)
#   sh install.sh --project  this project (./.claude/skills)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ "$1" = "--project" ]; then DEST=".claude/skills"; else DEST="$HOME/.claude/skills"; fi
mkdir -p "$DEST"
for d in "$HERE"/skills/insta*; do
  rm -rf "$DEST/$(basename "$d")"
  cp -R "$d" "$DEST/"
done
echo "skills -> $DEST"
if command -v pipx >/dev/null 2>&1; then
  pipx install --force "$HERE" >/dev/null && echo "igos installed with pipx"
else
  python3 -m pip install --user --quiet "$HERE" 2>/dev/null \
    || python3 -m pip install --user --quiet --break-system-packages "$HERE"
  echo "igos installed with pip --user (make sure ~/.local/bin is on PATH)"
fi
igos init 2>/dev/null || python3 "$HERE/igos_run.py" init
echo "done. In Claude, try: /insta-setup"
