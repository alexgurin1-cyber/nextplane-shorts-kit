#!/usr/bin/env python3
"""Host a finished vertical video publicly for Buffer (Supabase rendered_videos/social/<slug>.mp4).
usage: NP_SOCIAL_SECRET=... social_upload.py <slug> <video.mp4>   -> prints the public URL
slug must match ^[a-z0-9_]{2,60}$. Re-encodes audio to AAC 48 kHz (Instagram limit); video stream untouched."""
import json, os, subprocess, sys, tempfile, urllib.request
B = "https://uiprgookspqnvyumkyse.supabase.co"
# public anon key (safe to embed); the edge function also requires the x-np-secret header
ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVpcHJnb29rc3BxbnZ5dW1reXNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwNTMxNjAsImV4cCI6MjA5MTYyOTE2MH0.azwAiXWBrNDJrz0kMcq69n2K3PO4XIbncCbrz8iBXzA"
def main(slug, src):
    out = os.path.join(tempfile.gettempdir(), f"social_{slug}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    req = urllib.request.Request(B + "/functions/v1/social-upload-url", json.dumps({"slug": slug}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + ANON, "apikey": ANON,
                 "x-np-secret": os.environ["NP_SOCIAL_SECRET"]})
    r = json.load(urllib.request.urlopen(req, timeout=60))
    s = r["signedUrl"] if r["signedUrl"].startswith("http") else B + "/storage/v1" + r["signedUrl"]
    urllib.request.urlopen(urllib.request.Request(s, open(out, "rb").read(), method="PUT",
        headers={"Content-Type": "video/mp4", "x-upsert": "true"}), timeout=300).read()
    print(r["publicUrl"])
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
