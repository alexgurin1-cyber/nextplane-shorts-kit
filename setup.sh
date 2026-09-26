#!/bin/bash
# Prepare a cloud workspace for a NextPlane Short.
# Prereq: ~/.nextplane.env exists with ELEVENLABS_API_KEY, GEMINI_API_KEY, YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
#         (values come from memory: reference-elevenlabs-key, reference-gemini-key, reference-youtube-oauth).
# Usage: source setup.sh <topic_slug>     -> exports KIT, WORK, env vars; creates $WORK with fonts/ assets/ vo/ frames/ photos/
set -e
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; export KIT
[ -f ~/.nextplane.env ] || { echo "MISSING ~/.nextplane.env (write it from memory first)"; return 1 2>/dev/null || exit 1; }
set -a; . ~/.nextplane.env; set +a
for v in ELEVENLABS_API_KEY YT_CLIENT_ID YT_CLIENT_SECRET YT_REFRESH_TOKEN; do [ -n "${!v}" ] || echo "WARN: $v empty"; done
python3 -c "import PIL, numpy" 2>/dev/null || pip install -q --break-system-packages pillow numpy
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
SLUG="${1:-short}"; export WORK="/tmp/$SLUG"
mkdir -p "$WORK"/{fonts,assets,vo,frames,photos}
cp "$KIT"/fonts/*.ttf "$WORK/fonts/"; cp "$KIT/lib/endcard.py" "$WORK/"
cp "$KIT/assets/logo_for_dark_800.png" "$WORK/assets/logo.png"
echo "KIT=$KIT WORK=$WORK ready"; python3 "$KIT/lib/yt.py" auth
set +e
