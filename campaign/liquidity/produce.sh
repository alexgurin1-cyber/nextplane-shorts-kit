#!/bin/bash
# Produce one liquidity-campaign RANKING Short end to end. usage: produce.sh <slot 1-10> [upload]
set -eo pipefail
SLOT=$1; DO_UPLOAD=${2:-}
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; export KIT
set -a; . ~/.nextplane.env; set +a
SLUG=$(python3 "$KIT/campaign/liquidity/specs.py" $SLOT | python3 -c "import json,sys; print(json.load(sys.stdin)['slug'])")
export WORK=/tmp/$SLUG; mkdir -p $WORK/{fonts,assets,vo,frames,photos}
cp "$KIT"/fonts/*.ttf $WORK/fonts/; cp "$KIT/lib/endcard.py" $WORK/; cp "$KIT/assets/logo_for_dark_800.png" $WORK/assets/logo.png
cp "$KIT"/templates/ranking/*.py $WORK/
python3 "$KIT/campaign/liquidity/specs.py" $SLOT > $WORK/spec.json
cd $WORK
echo "== [$SLUG] photos"
for s in $(python3 -c "import json; d=json.load(open('spec.json')); print(' '.join(sorted(set([r['photo'] for r in d['rows']]+d['bg']))))"); do
  [ -f photos/$s-0.jpg ] || cp "$KIT/campaign/photo_cache/$s-0.jpg" photos/$s-0.jpg
done
echo "== [$SLUG] report capture"
TAIL=$(python3 -c "import json; print(json.load(open('spec.json'))['tail']['n'])")
if [ ! -f assets/report.png ]; then
  mkdir -p cap; CAP_W=1000 CAP_H=1000 timeout 300 python3 "$KIT/lib/report_capture.py" $TAIL cap >/dev/null 2>&1 || echo "capture failed for $TAIL"
  python3 "$KIT/campaign/liquidity/report_crop.py" cap assets/report.png || true
fi
echo "== [$SLUG] VO"
python3 gen_vo.py
TOTAL=$(python3 -c "
import os,sys; os.environ['WORK']='$WORK'; sys.argv=['x','0','0']; sys.path.insert(0,'$WORK'); import render; print(round(render.TOTAL,2))")
echo "TOTAL=$TOTAL"
[ -f music_el.mp3 ] || python3 gen_music.py $TOTAL
NF=$(python3 -c "import math; print(math.ceil($TOTAL*30))")
echo "== [$SLUG] render $NF frames"
for w in 0 1; do (python3 render.py $w $NF 2 >/dev/null 2>&1 || python3 render.py $w $NF 2) & done; wait
python3 render.py 0 $NF 1 | tail -1
echo "== [$SLUG] mux"
python3 mux.py
python3 "$KIT/qa/check_render.py" nextplane_$SLUG.mp4 --max-duration=110 || echo "QA FLAG"
if [ "$DO_UPLOAD" = "upload" ]; then
  python3 - <<EOF
import json
s=json.load(open("spec.json"))
desc = (s["title"] + ". " + s["subline"] + ", in NextPlane sold-listing data.\n\n"
        "Is your airplane liquid? Three numbers decide it: how long your model takes to sell, how often sellers cut the price before it sells, and how much it loses per year. "
        "The list tells you the model. The report tells you the airplane: price-cut history on that tail, days listed, owners, the federal accident record.\n\n"
        "Plug in any N-number: https://nextplane.us\n\n#aviation #generalaviation #aircraftforsale #nextplane #IsYourAirplaneLiquid")
json.dump({"title": s["yt_title"], "description": desc, "publishAt": s["publish"]}, open("meta.json","w"))
EOF
  python3 "$KIT/lib/yt.py" upload nextplane_$SLUG.mp4 meta.json ${SLUG}_yt_result.json
fi
echo "== [$SLUG] done"
