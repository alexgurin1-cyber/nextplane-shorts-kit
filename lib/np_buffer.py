#!/usr/bin/env python3
"""NextPlane -> Buffer helper (cloud runs). Needs env BUFFER_API_KEY.
  np_buffer.py post CHANNEL(ig|tt|li) VIDEO_URL DUE_ISO TEXT_FILE   -> prints post id
  np_buffer.py queue                                                -> lists scheduled posts per channel
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
if __name__ == "__main__":
    c = sys.argv[1]
    if c == "post": print(post(sys.argv[2], sys.argv[3], sys.argv[4], open(sys.argv[5]).read()))
    elif c == "queue":
        q = """query($o:OrganizationId!,$c:[ChannelId!]){posts(input:{organizationId:$o,filter:{channelIds:$c,status:[scheduled,error]}},first:50){edges{node{id status dueAt text}}}}"""
        for k,(cid,_) in CH.items():
            try:
                e = gql(q, {"o": ORG, "c": [cid]})["posts"]["edges"]
                print(k, [(n["node"]["status"], n["node"]["dueAt"], n["node"]["text"][:40]) for n in e])
            except Exception as ex: print(k, "queue query failed:", ex)
