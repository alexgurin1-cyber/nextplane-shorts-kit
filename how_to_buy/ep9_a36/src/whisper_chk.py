import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("tiny.en", compute_type="int8")
for b in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg","-v","error","-i",f"vo/{b}.mp3","-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32)/32768
    segs,_ = m.transcribe(a, language="en")
    print(b, " ".join(s.text.strip() for s in segs))
