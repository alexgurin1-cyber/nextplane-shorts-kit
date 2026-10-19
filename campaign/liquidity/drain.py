#!/usr/bin/env python3
"""Schedule liquidity-campaign static posts into Buffer.
  drain.py KEY [KEY...]      schedule these plan.json keys (prints 'key post_id')
  drain.py --auto            read table state from env SCHEDULED_KEYS (comma list, from
                             `select string_agg(key,',') from social_campaign_posts where post_id is not null`),
                             keep <=8 scheduled per channel, schedule earliest unscheduled first.
Needs BUFFER_API_KEY. Run from this directory (uses buffer_img.py)."""
import json, os, sys, subprocess, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
plan = json.load(open("plan.json"))
def queue_count(ch):
    cid = {"ig":"6abacf50ea19ca0bde1824b7","li":"6abacf80ea19ca0bde182637","tt":"6ac9066e6a5c39ccb662b515"}[ch]
    q = """query($o:OrganizationId!,$c:[ChannelId!]){posts(input:{organizationId:$o,filter:{channelIds:$c,status:[scheduled]}},first:50){edges{node{id}}}}"""
    r = urllib.request.Request("https://api.buffer.com", json.dumps({"query":q,"variables":{"o":"6abacdf71924df9de72a5a78","c":[cid]}}).encode(),
        headers={"Content-Type":"application/json","Authorization":"Bearer "+os.environ["BUFFER_API_KEY"]})
    return len(json.load(urllib.request.urlopen(r, timeout=60))["data"]["posts"]["edges"])
def sched(r):
    open("_cap.txt","w").write(r["text"])
    return subprocess.check_output(["python3","buffer_img.py",r["channel"],",".join(r["urls"]),r["due"],"_cap.txt"]).decode().strip()
if sys.argv[1:] == ["--auto"]:
    done = set(filter(None, os.environ.get("SCHEDULED_KEYS","").split(",")))
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for ch in ("ig","li"):
        room = 8 - queue_count(ch)
        todo = sorted([r for r in plan if r["channel"]==ch and r["key"] not in done and r["due"] > now], key=lambda r: r["due"])
        for r in todo[:max(room,0)]:
            print(r["key"], sched(r))
else:
    by = {r["key"]: r for r in plan}
    for k in sys.argv[1:]: print(k, sched(by[k]))
