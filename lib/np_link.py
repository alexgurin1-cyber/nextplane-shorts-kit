#!/usr/bin/env python3
"""NextPlane link rule (Alex, 2026-10-26): every post on every channel carries the report link.

  from np_link import with_link
  text = with_link(text, "instagram")      # idempotent: adds the link block only if absent

Per-channel tracked URL:  https://nextplane.us/aircraft-report?utm_source=<platform>&utm_medium=social
Instagram / TikTok do not make caption URLs tappable, so those captions also get a
"link in bio" line; the bio link on both profiles points at the same report page.
YouTube and LinkedIn make URLs clickable, so the URL alone is enough there.
"""
import re

BASE = "https://nextplane.us/aircraft-report"
PLATFORMS = ("youtube", "instagram", "tiktok", "linkedin")
BIO_LINE = "Run any N-number — link in bio."


def url(platform):
    if platform not in PLATFORMS:
        raise ValueError(f"unknown platform {platform!r}; expected one of {PLATFORMS}")
    return f"{BASE}?utm_source={platform}&utm_medium=social"


def has_link(text):
    # Only the tracked report link counts; a bare "nextplane.us" mention does not satisfy the rule.
    return "nextplane.us/aircraft-report?utm_source=" in text


def with_link(text, platform, position="end"):
    """Return text with the channel's link block. Idempotent.

    position="end"   (default) — link block appended after the body, before nothing else.
    position="top"   — YouTube: URL on line 2 (under the first takeaway line) AND after the body,
                       so it sits above the fold in the collapsed description.
    Hashtags already at the end of the text are kept after the link block so the IG 5-tag
    rule and tag discovery are unaffected.
    """
    text = text.rstrip()
    if has_link(text):
        return text
    # drop older hand-written link lines so the block is not duplicated
    text = "\n".join(l for l in text.split("\n")
                     if not re.search(r"link in (our )?bio|Look up any aircraft by N-number", l, re.I)).rstrip()
    link = url(platform)
    block = (BIO_LINE + "\n" + link) if platform in ("instagram", "tiktok") else link
    # keep a trailing hashtag line last
    lines = text.split("\n")
    tail = []
    while lines and lines[-1].strip() and all(w.startswith("#") for w in lines[-1].split()):
        tail.insert(0, lines.pop())
    body = "\n".join(lines).rstrip()
    if position == "top" and platform == "youtube":
        first, _, rest = body.partition("\n")
        body = first + "\n" + link + ("\n" + rest if rest else "")
    out = body + "\n\n" + block
    if tail:
        out += "\n\n" + "\n".join(tail)
    return out


if __name__ == "__main__":
    import sys
    print(with_link(sys.stdin.read(), sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "end"))
