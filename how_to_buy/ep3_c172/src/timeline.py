import json, sys
sys.path.insert(0, "/tmp/htb_c172"); from beats import BEATS
LEAD = 0.6; GAP = 0.75; END_PAUSE = 0.9; TAIL = 4.0
OFFS = {}; SCENES = []; t = LEAD
for i, (bid, scene, _) in enumerate(BEATS):
    d = json.load(open(f"/tmp/htb_c172/vo/{bid}.json"))["dur"]
    if bid == "b17": t += END_PAUSE - GAP
    start = t if i else 0.0
    OFFS[bid] = t
    t += d
    end = t + (GAP if bid != "b17" else TAIL)
    SCENES.append((bid, scene, start, end)); t = end
TOTAL = round(t, 2)
if __name__ == "__main__":
    for s in SCENES: print(s[0], s[1], round(s[2],2), round(s[3],2))
    print("TOTAL", TOTAL)
