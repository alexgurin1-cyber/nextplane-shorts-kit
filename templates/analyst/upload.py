#!/usr/bin/env python3
import json, os, urllib.request
tok=open("/tmp/bw/tok.txt").read().strip()
publish="2026-09-27T15:00:00Z"   # 2026-09-26T15:00Z already taken by W_7dT9vEgpI (panel_flip); next free daily 15:00Z slot
title="\"Complete logs.\" 449 sellers say it. It's worth $0."
desc="""Is your own ad's favorite phrase actually worth anything?

Run any tail number and see what a NextPlane report reads instead of the ad copy — the real maintenance and ownership record, not the seller's adjectives.

Before you call the broker, check the data at NextPlane.us
https://nextplane.us

NextPlane monitors every FAA transaction and thousands of live aircraft listings. Prices shown are asking prices, not sale prices.
Photos: Adrian Pingstone (public domain), Frank Schwichtenberg (CC BY 4.0), Huhu Uet (CC BY 3.0), Curimedia Photography (CC BY 2.0), via Wikimedia Commons.
#aviation #generalaviation #aircraftforsale #airplaneownership #nextplane"""
F="/tmp/bw/nextplane_buzzwords.mp4"
meta=json.dumps({"snippet":{"title":title,"description":desc,"categoryId":"2"},
 "status":{"privacyStatus":"private","publishAt":publish,"selfDeclaredMadeForKids":False}}).encode()
req=urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    data=meta, headers={"Authorization":f"Bearer {tok}","Content-Type":"application/json; charset=UTF-8",
    "X-Upload-Content-Type":"video/mp4","X-Upload-Content-Length":str(os.path.getsize(F))}, method="POST")
loc=urllib.request.urlopen(req,timeout=60).headers["Location"]
data=open(F,"rb").read()
r=json.load(urllib.request.urlopen(urllib.request.Request(loc, data=data, headers={"Authorization":f"Bearer {tok}","Content-Type":"video/mp4"}, method="PUT"),timeout=600))
out={"id":r.get("id"),"title":title,"publishAt":publish,"status":r.get("status")}
print(json.dumps(out,indent=1)); json.dump(out,open("/tmp/bw/buzzwords_yt_result.json","w"),indent=1)
