import json, os, sys, urllib.request
B="https://uiprgookspqnvyumkyse.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVpcHJnb29rc3BxbnZ5dW1reXNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwNTMxNjAsImV4cCI6MjA5MTYyOTE2MH0.azwAiXWBrNDJrz0kMcq69n2K3PO4XIbncCbrz8iBXzA"
def up(slug, path):
    req=urllib.request.Request(B+"/functions/v1/social-upload-url", json.dumps({"slug":slug,"ext":"png"}).encode(),
        headers={"Content-Type":"application/json","Authorization":"Bearer "+ANON,"apikey":ANON,"x-np-secret":os.environ["NP_SOCIAL_SECRET"]})
    r=json.load(urllib.request.urlopen(req,timeout=60))
    s=r["signedUrl"] if r["signedUrl"].startswith("http") else B+"/storage/v1"+r["signedUrl"]
    urllib.request.urlopen(urllib.request.Request(s, open(path,"rb").read(), method="PUT", headers={"Content-Type":"image/png","x-upsert":"true"}),timeout=120).read()
    return r["publicUrl"]
if __name__=="__main__":
    out={}
    for f in sorted(os.listdir("out")):
        slug="liq_"+f[:-4]; out[f]=up(slug,"out/"+f); print(f, out[f])
    json.dump(out, open("urls.json","w"), indent=1)
