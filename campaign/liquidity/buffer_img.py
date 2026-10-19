import json, os, sys, urllib.request, re
API="https://api.buffer.com"; KEY=os.environ["BUFFER_API_KEY"]
CH={"tt":("6ac9066e6a5c39ccb662b515","tiktok"),"ig":("6abacf50ea19ca0bde1824b7","instagram"),"li":("6abacf80ea19ca0bde182637","linkedin")}
def gql(q,v=None):
    r=urllib.request.Request(API,json.dumps({"query":q,"variables":v or {}}).encode(),headers={"Content-Type":"application/json","Authorization":f"Bearer {KEY}"})
    d=json.load(urllib.request.urlopen(r,timeout=90))
    if d.get("errors"): raise RuntimeError(json.dumps(d["errors"])[:800])
    return d["data"]
MUT="""mutation($input: CreatePostInput!){ createPost(input:$input){ ... on PostActionSuccess { post { id dueAt } } ... on MutationError { message } } }"""
def post(ch, urls, due, text):
    cid,svc=CH[ch]
    if svc=="instagram" and len(re.findall(r"#\w+",text))>5: raise SystemExit("IG max 5 hashtags")
    inp={"text":text,"channelId":cid,"schedulingType":"automatic","mode":"customScheduled","dueAt":due,
         "assets":[{"image":{"url":u}} for u in urls]}
    if svc=="instagram": inp["metadata"]={"instagram":{"type":"post","shouldShareToFeed":True}}
    r=gql(MUT,{"input":inp})["createPost"]
    if "message" in r: raise RuntimeError(r["message"])
    return r["post"]["id"]
if __name__=="__main__":
    print(post(sys.argv[1], sys.argv[2].split(","), sys.argv[3], open(sys.argv[4]).read()))
