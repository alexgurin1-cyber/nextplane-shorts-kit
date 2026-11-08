-- NUMBER clips (RUNBOOK_SHORTS15.md section 4c). One query per kind. Run with the Supabase execute_sql tool after
-- replacing the two placeholders by hand:
--   {category}  piston_single | piston_twin | turboprop      (never jet: no jet prices or jet clips)
--   {model_re}  regex on upper(make||' '||model); '.' = the whole category, e.g. 'SR ?-?20' (Cirrus SR20),
--               '172' (Cessna 172 family), '(PA-28|PA28|WARRIOR|ARCHER|CHEROKEE)' (Piper PA-28), 'SR ?-?22', 'BONANZA|A36|G36|F33|V35'
-- Base for every kind: currently listed, US, with an N-number, one row per tail (cross-site duplicates removed).
-- Statement timeouts: keep the CTEs materialized and run one kind per call.

-- ===================== 1. DAMAGE HISTORY =====================
-- damage_history_total = ad discloses damage (parsed damage field true) OR a federal accident record (NTSB) with
-- substantial damage / destroyed whose serial number matches the listing's serial (tier A; registration alone is NOT
-- enough - N-numbers are reused). record_ad_silent = record matched AND the ad's damage field is false
-- (say "the ad doesn't mention it", never "the ad hides it" or "the seller lied").
with base as materialized (
  select distinct on (upper(registration)) upper(registration) reg, serial_number, damage_history
  from aircraft_listings
  where status='active' and registration ~* '^N[0-9]' and location_country in ('US','USA')
    and category = '{category}' and upper(make||' '||model) ~ '{model_re}'
  order by upper(registration), (source='controller') desc
), n as materialized (
  select upper(regis_no) reg, damage, upper(regexp_replace(coalesce(acft_serial_no,''),'[^A-Za-z0-9]','','g')) sn
  from ntsb_accidents where regis_no ~* '^N[0-9]'
), x as (
  select b.*, exists (select 1 from n where n.reg=b.reg and n.damage in ('SUBS','DEST') and n.sn<>''
                      and n.sn = upper(regexp_replace(coalesce(b.serial_number,''),'[^A-Za-z0-9]','','g'))) rec
  from base b)
select count(*) for_sale,
  count(*) filter (where damage_history) ad_discloses,
  count(*) filter (where rec) federal_record_serial_matched,
  count(*) filter (where rec and not coalesce(damage_history,false)) record_ad_silent,
  count(*) filter (where damage_history or rec) damage_history_total
from x;

-- ===================== 2. TRAINING HISTORY =====================
-- "Signs it spent part of its life as a trainer or rental": at least one of
--   hi_hours      averaged more than 250 airframe hours a year since built (builds 1940-2025 with hours > 0)
--   ad_hist       the ad says so in history words (flight school, leaseback, Part 141, flying club, rental fleet...),
--                 negations excluded ("never a rental"). Suitability phrases ("would make a great trainer") do NOT count.
--   school_owner  the current FAA registrant is a school, academy, university, college or flying club
--   inst_record   a federal accident record (any damage) flown as instruction, serial-matched
-- Read 5 matched ad_hist snippets before voicing (substring(listing_description from '(?i).{0,60}(flight school|leaseback).{0,40}')).
-- 2026-11-05 row check (SR20): ad_hist was 5 of 5 false hits - negations the regex misses ("never used for flight training",
--   "no worries about ... flight school abuse") and offers/suitability ("Lease back Opportunity", "ideal for leaseback to
--   flight school", "great option for ... flight school"). Count ad_hist tails only after reading each snippet; drop the
--   ones that do not describe the airplane's past. hi_hours now needs builds <= current year - 2: with a 1-year floor a
--   2025 airplane with 330 h counted as a trainer (5 SR20s dropped). See DATA_20261105.md.
with base as materialized (
  select distinct on (upper(registration)) upper(registration) reg, substr(upper(registration),2) nn, serial_number,
         year, total_time_airframe ttaf, coalesce(listing_description,'') d
  from aircraft_listings
  where status='active' and registration ~* '^N[0-9]' and location_country in ('US','USA')
    and category = '{category}' and upper(make||' '||model) ~ '{model_re}'
  order by upper(registration), (source='controller') desc
), s as materialized (
  select b.nn from base b join aircraft_master m on m.n_number=b.nn
  where m.name ~* '(FLIGHT SCHOOL|FLIGHT TRAINING|ACADEMY|UNIVERSITY|COLLEGE|FLYING CLUB|AERO CLUB|FLIGHT CENTER|AVIATION TRAINING|PILOT TRAINING|SCHOOL)'
), i as materialized (
  select upper(regis_no) reg, upper(regexp_replace(coalesce(acft_serial_no,''),'[^A-Za-z0-9]','','g')) sn
  from ntsb_accidents where type_fly='INST' and regis_no ~* '^N[0-9]'
), f as (
  select b.*,
    (ttaf > 0 and year between 1940 and extract(year from current_date)::int - 2 and ttaf::numeric / greatest(extract(year from current_date)::int - year, 1) > 250) hi_hours,
    (d ~* '(flight school|leaseback|lease back|part 141|flying club|club (aircraft|airplane|plane)|rental (history|fleet|aircraft|airplane|use)|used (for|in|as a) (flight )?(training|trainer|rental)|training fleet|school (aircraft|airplane|plane))'
       and d !~* '(never|no|not|non)[ -](been )?(a |used (as|for|in) (a )?)?(flight school|rental|leaseback|lease back|trainer|training)') ad_hist,
    (b.nn in (select nn from s)) school_owner,
    exists (select 1 from i where i.reg=b.reg and i.sn<>'' and i.sn = upper(regexp_replace(coalesce(b.serial_number,''),'[^A-Za-z0-9]','','g'))) inst_record
  from base b)
select count(*) for_sale,
  count(*) filter (where hi_hours or ad_hist or school_owner or inst_record) training_signs,
  count(*) filter (where hi_hours) hi_hours, count(*) filter (where ad_hist) ad_hist,
  count(*) filter (where school_owner) school_owner, count(*) filter (where inst_record) inst_record
from f;

-- ===================== 3. SELLER OWNERSHIP (how long the seller has owned it) =====================
-- FAA certificate issue date of the current registrant = when the seller registered it (survives FAA renewals,
-- verified 2026-08-04). Guardrails: cert year >= build year - 1 (N-number reuse), cert date <= listing first seen
-- (otherwise the buyer already re-registered it), builds <= 2024 (factory inventory), no REGISTRATION PENDING /
-- SALE REPORTED registrants. Tenure is context, not a verdict: never imply a short hold means a problem.
with base as materialized (
  select distinct on (upper(registration)) upper(registration) reg, substr(upper(registration),2) nn, year, created_at
  from aircraft_listings
  where status='active' and registration ~* '^N[0-9]' and location_country in ('US','USA') and year <= 2024
    and category = '{category}' and upper(make||' '||model) ~ '{model_re}'
  order by upper(registration), (source='controller') desc
), j as (
  select b.*, case when m.cert_issue_date ~ '^\d{8}$' then to_date(m.cert_issue_date,'YYYYMMDD') end cid
  from base b join aircraft_master m on m.n_number=b.nn
  where m.name !~* '(REGISTRATION PENDING|SALE REPORTED)'
)
select count(*) filter (where cid is not null and extract(year from cid) >= year - 1 and cid <= created_at::date) with_cert,
  count(*) filter (where cid is not null and extract(year from cid) >= year - 1 and cid <= created_at::date and cid >= current_date - 730) owned_under_2y,
  count(*) filter (where cid is not null and extract(year from cid) >= year - 1 and cid <= created_at::date and cid >= current_date - 365) owned_under_1y,
  percentile_cont(0.5) within group (order by (current_date - cid) / 365.25)
    filter (where cid is not null and extract(year from cid) >= year - 1 and cid <= created_at::date) median_years
from j;

-- ===================== 4. PRICED HIGHER (Alex 2026-11-03: "for sale before at one price and now it's higher") =====================
-- Current ask is at least 1% above (a) this ad's own first recorded ask, or (b) the last price of an earlier, closed ad
-- for the same tail. Raises over +60% are excluded as data errors. Raw +price events inside an ad are NOT used: many are a
-- cut that was reverted (e.g. 124 raw vs 27 strict for singles on 2026-11-03). Row-check 5 tails before voicing.
with base as materialized (
  select distinct on (upper(registration)) upper(registration) reg, listing_id, asking_price_usd p,
         original_asking_price_usd p0, created_at
  from aircraft_listings
  where status='active' and registration ~* '^N[0-9]' and location_country in ('US','USA') and asking_price_usd > 1000
    and category = '{category}' and upper(make||' '||model) ~ '{model_re}'
  order by upper(registration), (source='controller') desc
), up_same as (
  select reg from base where p0 > 1000 and p > p0 * 1.01 and p < p0 * 1.6
), up_prev as (
  select distinct b.reg from base b join aircraft_listings o on upper(o.registration)=b.reg and o.listing_id<>b.listing_id
    and o.status<>'active' and coalesce(o.delisted_at, o.last_seen_at) < b.created_at
    and coalesce(o.last_known_price, o.asking_price_usd) between 1000 and b.p / 1.01
    and b.p < coalesce(o.last_known_price, o.asking_price_usd) * 1.6
)
select count(*) for_sale,
  count(*) filter (where reg in (select reg from up_same)) above_own_first_ask,
  count(*) filter (where reg in (select reg from up_prev)) above_earlier_ad,
  count(*) filter (where reg in (select reg from up_same) or reg in (select reg from up_prev)) priced_higher
from base;

-- ===================== 4b. PRICED HIGHER — strict (2026-11-08, use this one) =====================
-- Fixes found on the 2026-11-08 row check (DATA_20261108.md): original_asking_price_usd is overwritten on raises and can hold
-- a cut price, so the first ask comes from the earliest aircraft_price_history row; first prices that held < 3 days are
-- scrape glitches; asks under half the model median (>= 3 for sale) are shares / parse errors and leave the base too;
-- only tails seen in the last 7 days. Still read every counted tail with an implausible first ask (>40% jump) before voicing.
with base0 as materialized (
  select distinct on (upper(registration)) upper(registration) reg, listing_id, asking_price_usd p,
         original_asking_price_usd p0, created_at, last_seen_at, make, model
  from aircraft_listings
  where status='active' and registration ~* '^N[0-9]' and location_country in ('US','USA') and asking_price_usd > 1000
    and category = '{category}' and upper(make||' '||model) ~ '{model_re}'
  order by upper(registration), (source='controller') desc
), med as (select make, model, percentile_cont(0.5) within group (order by p) m, count(*) n from base0 group by 1,2),
base as materialized (
  select b.*, coalesce(h.old_price, b.p0) first_ask, h.recorded_at first_change
  from base0 b left join med on med.make=b.make and med.model=b.model
  left join lateral (select old_price, recorded_at from aircraft_price_history h where h.listing_id=b.listing_id order by recorded_at limit 1) h on true
  where b.last_seen_at > now() - interval '7 days' and not (med.n >= 3 and b.p < 0.5*med.m)
), up_same as (
  select reg from base where first_ask > 1000 and p > first_ask * 1.01 and p < first_ask * 1.6
    and (first_change is null or first_change >= created_at + interval '3 days')
), up_prev as (
  select distinct b.reg from base b join aircraft_listings o on upper(o.registration)=b.reg and o.listing_id<>b.listing_id
    and o.status<>'active' and coalesce(o.delisted_at, o.last_seen_at) < b.created_at
    and coalesce(o.last_known_price, o.asking_price_usd) between 1000 and b.p / 1.01
    and b.p < coalesce(o.last_known_price, o.asking_price_usd) * 1.6
)
select count(*) for_sale,
  count(*) filter (where reg in (select reg from up_same)) above_own_first_ask,
  count(*) filter (where reg in (select reg from up_prev)) above_earlier_ad,
  count(*) filter (where reg in (select reg from up_same) or reg in (select reg from up_prev)) priced_higher,
  string_agg(reg, ',' order by reg) filter (where reg in (select reg from up_same) or reg in (select reg from up_prev)) tails
from base;
