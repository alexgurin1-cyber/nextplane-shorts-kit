#!/usr/bin/env python3
"""YouTube helper for NextPlane Shorts (cloud-safe; no local files needed).

Credentials come from environment variables (loaded by setup.sh from ~/.nextplane.env):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

Usage:
  yt.py auth                      -> prints channel title (verifies credentials)
  yt.py slots [n]                 -> lists the last n uploads with privacy/publishAt
  yt.py next-slot                 -> next free daily 15:00Z publish slot >= now+24h
  yt.py upload <mp4> <meta.json>  -> resumable private upload with publishAt
       meta.json = {"title": ..., "description": ..., "publishAt": "optional ISO8601Z"}
       prints and returns {"id", "title", "publishAt", "status", "studio_url"}
"""
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/youtube/v3"


def token():
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    r = urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=body), timeout=30)
    return json.load(r)["access_token"]


def get(path, tok):
    req = urllib.request.Request(f"{API}/{path}", headers={"Authorization": f"Bearer {tok}"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def recent(tok, n=25):
    ch = get("channels?part=contentDetails,snippet&mine=true", tok)
    up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = get(f"playlistItems?part=contentDetails&playlistId={up}&maxResults={min(n, 50)}", tok)
    ids = ",".join(i["contentDetails"]["videoId"] for i in pl.get("items", []))
    if not ids:
        return []
    v = get(f"videos?part=snippet,status&id={ids}", tok)
    return [{"id": it["id"], "privacy": it["status"]["privacyStatus"],
             "publishAt": it["status"].get("publishAt"), "title": it["snippet"]["title"]} for it in v["items"]]


def next_slot(tok):
    taken = {x["publishAt"][:10] for x in recent(tok, 50) if x.get("publishAt")}
    now = dt.datetime.now(dt.timezone.utc)
    day = (now + dt.timedelta(hours=24)).date()
    while True:
        cand = dt.datetime.combine(day, dt.time(15, 0), tzinfo=dt.timezone.utc)
        if cand >= now + dt.timedelta(hours=24) and day.isoformat() not in taken:
            return cand.strftime("%Y-%m-%dT%H:%M:%SZ")
        day += dt.timedelta(days=1)


def upload(mp4, meta_path):
    tok = token()
    meta = json.load(open(meta_path))
    publish = meta.get("publishAt") or next_slot(tok)
    body = json.dumps({
        "snippet": {"title": meta["title"], "description": meta["description"], "categoryId": "2"},
        "status": {"privacyStatus": "private", "publishAt": publish, "selfDeclaredMadeForKids": False},
    }).encode()
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        data=body, method="POST",
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(os.path.getsize(mp4))})
    loc = urllib.request.urlopen(req, timeout=60).headers["Location"]
    with open(mp4, "rb") as fh:
        data = fh.read()
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        loc, data=data, method="PUT", headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"}), timeout=900))
    out = {"id": r.get("id"), "title": meta["title"], "publishAt": publish, "status": r.get("status"),
           "studio_url": f"https://studio.youtube.com/video/{r.get('id')}/edit"}
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "auth"
    if cmd == "auth":
        t = token()
        ch = get("channels?part=snippet&mine=true", t)
        print("OK channel:", ch["items"][0]["snippet"]["title"])
    elif cmd == "slots":
        for x in recent(token(), int(sys.argv[2]) if len(sys.argv) > 2 else 12):
            print(x["id"], x["privacy"], x["publishAt"] or "-", "|", x["title"][:60])
    elif cmd == "next-slot":
        print(next_slot(token()))
    elif cmd == "upload":
        res = upload(sys.argv[2], sys.argv[3])
        if len(sys.argv) > 4:
            json.dump(res, open(sys.argv[4], "w"), indent=1)
    else:
        print(__doc__)
        sys.exit(2)
