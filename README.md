# nextplane-shorts-kit

Production kit for NextPlane YouTube Shorts. The weekday scheduled task clones it into a Claude cloud session, so the Mac does not need to be on.

- `RUNBOOK.md`: the full procedure the scheduled run follows
- `setup.sh`: prepares a workspace (fonts, logo, end card, environment, YouTube authentication check)
- `lib/yt.py`: YouTube authentication, recent uploads, next free publish slot, resumable private upload
- `lib/photos.py`: license-safe photo fetch (Commons first, then Flickr through Openverse)
- `lib/footage.py` and `footage/index.json`: screened real-footage library (Pexels, Pixabay); clips are fetched from source on demand, not stored here
- `lib/endcard.py`: canonical end card
- `qa/check_render.py`: QA gate; `qa/smoke_test.py`: zero-cost environment check
- `templates/`: the latest reference scripts for each of the five formats
- `brand/`, `assets/`, `fonts/`: brand system, logo, Barlow Condensed and Space Mono (OFL)

Secrets are never stored here. Runs read them from Claude memory into `~/.nextplane.env`.
