"""Assemble /tmp/htb_sr22/cap: element captures (2x) + extras, with one sections.json of text boxes (CSS px)."""
import json, shutil, os
from PIL import Image
R = "/tmp/htb_sr22"; C = f"{R}/cap"; os.makedirs(C, exist_ok=True)
S = json.load(open(f"{R}/el/sections.json"))
for k in S: shutil.copy(f"{R}/el/{k}.png", f"{C}/{k}.png")
X = json.load(open(f"{R}/ex/sections.json")); shutil.copy(f"{R}/ex/before.png", f"{C}/before.png"); S["before"] = X["before"]
shutil.copy(f"{R}/upd/val_after.png", f"{C}/valafter.png"); S["valafter"] = json.load(open(f"{R}/upd/val_after.json"))
L = json.load(open(f"{R}/cl/sections.json"))
for k in L: shutil.copy(f"{R}/cl/{k}.png", f"{C}/{k}.png"); S[k] = L[k]
h, v = Image.open(f"{C}/header.png"), Image.open(f"{C}/verdict.png")
comb = Image.new("RGB", (h.width, h.height + v.height), (243, 240, 236)); comb.paste(h, (0, 0)); comb.paste(v, (0, h.height)); comb.save(f"{C}/_headercomb.png")
off = h.height / 2
S["_headercomb"] = {"w": 1152, "h": (h.height + v.height) / 2, "boxes": S["header"]["boxes"] + [dict(b, y=b["y"] + off) for b in S["verdict"]["boxes"]]}
json.dump(S, open(f"{C}/sections.json", "w"))
print("ok", len(S))
