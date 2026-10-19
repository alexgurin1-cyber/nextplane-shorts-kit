import json,os,sys,urllib.request,base64
K=os.environ["GEMINI_API_KEY"]
BASE="Instrumental only, no vocals. Confident mid-tempo analytical underscore for an aviation buyer's guide documentary, 96 BPM, warm and modern: muted electric bass pulse, tight rimshot and shaker, warm Rhodes chords, soft plucked guitar arpeggio, light airy pads, steady energy with gentle lifts, no prominent melody hook, key of A major. About 3 minutes long."
V={"m2":", slightly fuller arrangement with added light pads, same tempo and key","m3":", a touch more rhythmic drive with a subtle synth pulse, same tempo and key","m4":", same groove building a notch, then resolves warmly and ends cleanly in the final 10 seconds, instrumental"}
k=sys.argv[1]
body=json.dumps({"contents":[{"parts":[{"text":BASE+V[k]}]}]}).encode()
r=json.load(urllib.request.urlopen(urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/lyria-3-pro-preview:generateContent",data=body,headers={"x-goog-api-key":K,"Content-Type":"application/json"}),timeout=590))
for c in r["candidates"]:
  for p in c["content"]["parts"]:
    if "inlineData" in p: open(k+".mp3","wb").write(base64.b64decode(p["inlineData"]["data"])); print(k,"ok")
