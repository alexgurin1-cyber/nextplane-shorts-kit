-- Monthly PRICE CUTS set (first-of-the-month): distinct US airplanes with a price cut of >=1% recorded in each month,
-- by category, plus the live count for sale. Run on the 1st for the three months ending yesterday. :m0 = first day of the
-- earliest month, :m1 = first day of the month after the one just ended (e.g. '2026-09-01' and '2026-12-01' on Dec 1).
with c as (
  select al.category, date_trunc('month', h.recorded_at)::date m, coalesce(al.registration, al.listing_id::text) tail
  from aircraft_price_history h
  join analytics_listings al on al.listing_id = h.listing_id
  join aircraft_listings l on l.listing_id = h.listing_id
  where h.new_price < h.old_price and h.change_pct <= -1
    and h.recorded_at >= :m0 and h.recorded_at < :m1
    and (coalesce(l.location_country,'') in ('US','USA','United States','United States of America')
         or (l.location_country is null and al.registration ~ '^N'))
), a as (
  select al.category, count(distinct coalesce(al.registration, al.listing_id::text)) active
  from analytics_listings al join aircraft_listings l using (listing_id)
  where al.is_active_listing
    and (coalesce(l.location_country,'') in ('US','USA','United States','United States of America')
         or (l.location_country is null and al.registration ~ '^N'))
  group by 1)
select c.category, c.m, count(distinct tail) airplanes_cut, a.active
from c join a using (category)
where c.category in ('piston_single','piston_twin','turboprop')
group by 1,2,4 order by 1,2;
