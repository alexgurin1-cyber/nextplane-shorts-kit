# PRICE CUTS monthly set — October 2026 edition (produced 2026-10-30)

Alex, 2026-10-30: one 15-second clip per category (single / twin / turboprop) on how many airplanes got a price cut last
month versus the month before; standing first-of-the-month set, consecutive days, TikTok + Instagram at 16:00Z.

Query: `price_cuts.sql` (m0 = 2026-08-01, m1 = 2026-11-01, run 2026-10-30 19:05Z — October therefore covers the 1st–30th).
Definition: distinct airplanes (not cut events; a tail cut twice counts once) with a recorded cut of at least 1%,
US listings (country US, or country null with an N-registration), from `aircraft_price_history` × `analytics_listings`.

| Category | Aug | Sep | Oct | For sale now | Share cut in Oct |
|---|---|---|---|---|---|
| Single-engine piston | 581 | 575 | 615 | 3,287 | 18.7% → "1 in 5" |
| Piston twin | 85 | 76 | 89 | 512 | 17.4% → "1 in 6" |
| Turboprop | 27 | 31 | 48 | 478 | 10.0%; +55% on Sep → "up 55% on September" |

Wording rule (from the 2026-10-30 review): say "airplanes that got a price cut", never "cuts"; claim a rise only where the
month-over-month change is large (turboprops +55%); for singles and twins state the two counts and let the viewer compare.

Clips: `nextplane15_cuts_single.mp4` 14.87 s, `cuts_twin` 11.67 s (re-muxed with alimiter 0.6 — true peak was +0.5 dBTP
at 0.75), `cuts_turboprop` 12.27 s; all −13.7 to −14.3 LUFS. Photos (Openverse/Flickr): single hook Dylan Agbagni (CC0,
N352RC SR22, registration blurred), find D. Miller (CC BY 2.0, Archer II); twin hook Mark Harkin (CC BY 2.0, Beech 58,
reg blurred), find James Walsh (CC BY 2.0, Cessna 310); turboprop hook Mark Harkin (CC BY 2.0, PC-12, reg blurred),
find Photographer 192 (CC BY 2.0, PC-12).

Buffer (Nov 2/3/4 16:00Z, TikTok + Instagram): single 6ae4ec6998505e7f522d73c5 / 6ae4ec69260ad0ee5bc52346;
twin 6ae4ec6a98505e7f522d748e / 6ae4ec6ba351214acfa55694; turboprop 6ae4ec6ca351214acfa556d1 / 6ae4ec6d10a950f1373d9c29.
Logged in `public.social_campaign_posts` (campaign = price_cuts_monthly), not in `social_shorts15`, whose primary key is
run_date and is owned by the daily clip run.
