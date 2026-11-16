#!/usr/bin/env python3
"""NextPlane -> Buffer helper (cloud runs). Needs env BUFFER_API_KEY.
  np_buffer.py post CHANNEL(ig|tt|li) VIDEO_URL DUE_ISO TEXT_FILE   -> prints post id
  np_buffer.py queue [POST_ID...]                                  -> lists scheduled posts per channel (+ full text of POST_IDs)
  np_buffer.py slot [YYYY-MM-DD]                                   -> 9:00 AM Pacific as UTC ISO (16:00Z PDT / 17:00Z PST)
  np_buffer.py freeday [START_YYYY-MM-DD]                           -> SLOT FIRST rule (2026-11-15): first Pacific day, from
                                                                     START (default tomorrow), whose morning slot is free on
                                                                     BOTH tt and ig; prints day, weekday, slot ISO, queue counts
  np_buffer.py fix POST_ID CHANNEL VIDEO_URL OLD NEW                -> replace OLD with NEW in a scheduled post's text
                                                                     (Buffer's editPost needs the video asset and IG reel type re-sent)
"""
import json, os, sys, urllib.request
API = "https://api.buffer.com"; KEY = os.environ["BUFFER_API_KEY"]
ORG = "6abacdf71924df9de72a5a78"
CH = {"tt": ("6ac9066e6a5c39ccb662b515", "tiktok"), "ig": ("6abacf50ea19ca0bde1824b7", "instagram"),
      "li": ("6abacf80ea19ca0bde182637", "linkedin")}
def gql(q, v=None):
    r = urllib.request.Request(API, json.dumps({"query": q, "variables": v or {}}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    d = json.load(urllib.request.urlopen(r, timeout=90))
    if d.get("errors"): raise RuntimeError(json.dumps(d["errors"])[:800])
    return d["data"]
MUT = """mutation($input: CreatePostInput!){ createPost(input:$input){
  ... on PostActionSuccess { post { id dueAt } } ... on MutationError { message } } }"""
def post(ch, url, due, text):
    cid, svc = CH[ch]
    # Link rule (2026-10-26): every post carries the tracked report link; added here if the caption lacks it.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from np_link import with_link
    text = with_link(text, svc)
    if svc == "instagram":
        import re
        if len(re.findall(r"#\w+", text)) > 5: raise SystemExit("Instagram allows max 5 hashtags")
    inp = {"text": text, "channelId": cid, "schedulingType": "automatic", "mode": "customScheduled",
           "dueAt": due, "assets": [{"video": {"url": url, "metadata": {"thumbnailOffset": 1500}}}]}
    if svc == "instagram": inp["metadata"] = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
    r = gql(MUT, {"input": inp})["createPost"]
    if "message" in r: raise RuntimeError(r["message"])
    return r["post"]["id"]
EDIT = """mutation($input: EditPostInput!){ editPost(input:$input){
  ... on PostActionSuccess { post { id dueAt text } } ... on MutationError { message } } }"""
def fix(pid, ch, url, old, new):
    """Correct a caption already in the queue (e.g. a missed photo credit) without deleting and re-posting."""
    q = """query($o:OrganizationId!,$c:[ChannelId!]){posts(input:{organizationId:$o,filter:{channelIds:$c,status:[scheduled]}},first:50){edges{node{id text}}}}"""
    cur = [e["node"]["text"] for e in gql(q, {"o": ORG, "c": [CH[ch][0]]})["posts"]["edges"] if e["node"]["id"] == pid]
    if not cur or old not in cur[0]: raise SystemExit(f"{pid}: post not scheduled or text not found")
    inp = {"id": pid, "text": cur[0].replace(old, new, 1), "assets": [{"video": {"url": url, "metadata": {"thumbnailOffset": 1500}}}]}
    if CH[ch][1] == "instagram": inp["metadata"] = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
    r = gql(EDIT, {"input": inp})["editPost"]
    if "message" in r: raise RuntimeError(r["message"])
    return r["post"]["id"]
def slot(day):
    """9:00 AM America/Los_Angeles on `day` (date) as a UTC ISO string."""
    import datetime as dt
    from zoneinfo import ZoneInfo
    t = dt.datetime.combine(day, dt.time(9, 0), ZoneInfo("America/Los_Angeles"))
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
def scheduled(ch):
    q = """query($o:OrganizationId!,$c:[ChannelId!]){posts(input:{organizationId:$o,filter:{channelIds:$c,status:[scheduled]}},first:50){edges{node{id dueAt}}}}"""
    return [e["node"]["dueAt"] for e in gql(q, {"o": ORG, "c": [CH[ch][0]]})["posts"]["edges"]]
def freeday(start=None):
    """A Pacific day's morning slot counts as taken when a post is due 15:00Z-18:59Z that day (older posts sit at
    16:00Z, which is 8 AM during standard time; treat them as that day's morning clip)."""
    import datetime as dt
    from zoneinfo import ZoneInfo
    pt = ZoneInfo("America/Los_Angeles")
    start = start or (dt.datetime.now(pt).date() + dt.timedelta(days=1))
    taken, counts = set(), {}
    for ch in ("tt", "ig"):
        due = scheduled(ch); counts[ch] = len(due)
        for d in due:
            u = dt.datetime.fromisoformat(d.replace("Z", "+00:00"))
            if 15 <= u.hour <= 18: taken.add((ch, u.astimezone(pt).date()))
    day = start
    while ("tt", day) in taken or ("ig", day) in taken: day += dt.timedelta(days=1)
    return day, counts
if __name__ == "__main__":
    c = sys.argv[1]
    if c == "slot":
        import datetime as dt; print(slot(dt.date.fromisoformat(sys.argv[2]))); sys.exit()
    if c == "freeday":
        import datetime as dt
        d, n = freeday(dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else None)
        print(d.isoformat(), d.strftime("%A"), slot(d), "queued:", n); sys.exit()
    if c == "fix": print(fix(*sys.argv[2:7]))
    elif c == "post": print(post(sys.argv[2], sys.argv[3], sys.argv[4], open(sys.argv[5]).read()))
    elif c == "queue":
        q = """query($o:OrganizationId!,$c:[ChannelId!]){posts(input:{organizationId:$o,filter:{channelIds:$c,status:[scheduled,error]}},first:50){edges{node{id status dueAt text}}}}"""
        for k,(cid,_) in CH.items():
            try:
                e = gql(q, {"o": ORG, "c": [cid]})["posts"]["edges"]
                print(k, [(n["node"]["status"], n["node"]["dueAt"], n["node"]["text"][:40]) for n in e])
                for n in e:   # `queue ID...` also prints the full text of those posts (link-rule check)
                    if n["node"]["id"] in sys.argv[2:]: print("--", n["node"]["id"], "\n" + n["node"]["text"])
            except Exception as ex: print(k, "queue query failed:", ex)
