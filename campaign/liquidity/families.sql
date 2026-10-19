-- Liquidity campaign single-metric rankings (family merge v2). Run against a snapshot table of sold listings
-- (create table scratch_sold_listings_<date> as select ... from analytics_listings where is_sold).
with base as (
  select category, make, upper(coalesce(nullif(model_family,''), model_raw)) mf, upper(model_raw) mr, year, last_price, days_on_market, coalesce(reduction_pct,0) red
  from scratch_sold_listings_20261018
  where year between 1970 and 2024 and category in ('jet','turboprop','piston_twin','piston_single')
    and last_price >= case when category in ('jet','turboprop') then 150000 else 20000 end and days_on_market is not null),
fam as (select *, case
   when mf ~ '^CITATION CJ1' then 'Citation CJ1/CJ1+' when mf ~ '^CITATION CJ2' then 'Citation CJ2/CJ2+' when mf ~ '^CITATION CJ3' then 'Citation CJ3/CJ3+'
   when mf ~ '^CITATION CJ4' then 'Citation CJ4' when mf ~ '^CITATION M2' then 'Citation M2' when mf ~ '^CITATION SOVEREIGN' then 'Citation Sovereign'
   when mf ~ '^CITATION (EXCEL|XLS)' then 'Citation Excel/XLS' when mf ~ '^CITATION (V|V ULTRA|ENCORE|ULTRA)$' then 'Citation V/Ultra/Encore'
   when mf ~ '^CITATION (I|ISP|II|SII|S/II|I SP)$' then 'Citation I/II/SII' when mf ~ '^CITATION BRAVO' then 'Citation Bravo' when mf ~ '^CITATION JET' then 'CitationJet 525'
   when mf ~ '^CITATION MUSTANG' then 'Citation Mustang' when mf ~ '^CITATION X' then 'Citation X' when mf ~ '^CITATION LATITUDE' then 'Citation Latitude'
   when mf ~ '^CIRRUS-SF50' then 'Cirrus Vision Jet' when mf ~ '^PHENOM 100' then 'Phenom 100/100E' when mf ~ '^PHENOM 300' then 'Phenom 300/300E'
   when mf ~ '^CHALLENGER 3[05]0' then 'Challenger 300/350' when mf ~ '^CHALLENGER 60[45]' then 'Challenger 604/605'
   when mf ~ '^GLOBAL (5000|6000|6500)' then 'Global 5000/6000/6500' when mf ~ '^GLOBAL EXPRESS' then 'Global Express/XRS'
   when mf ~ '^FALCON 2000' then 'Falcon 2000 family' when mf ~ '^FALCON 900' then 'Falcon 900 family' when mf ~ '^FALCON (7X|8X)' then 'Falcon 7X/8X' when mf ~ '^FALCON 50' then 'Falcon 50/50EX'
   when mf ~ '^(800|850|900)XP|^800A' then 'Hawker 800/850/900XP' when mf ~ '^400(A|XP)|NEXTANT' then 'Beechjet 400A/400XP' when mf ~ '^PREMIER' then 'Premier I/IA' when mf ~ '^HONDAJET' then 'HondaJet'
   when mf ~ '^45' and make='LEARJET' then 'Learjet 45/45XR' when mf ~ '^60' and make='LEARJET' then 'Learjet 60/60XR' when mf ~ '^GIV' then 'Gulfstream GIV/GIV-SP'
   when make='GULFSTREAM' and mr ~ '^G(550|500|450|280|200|150|650|700)' then 'Gulfstream '||substring(mr from '^G\d+')
   when mf ~ '^KING AIR (200|B200|250)' then 'King Air 200/B200/250' when mf ~ '^KING AIR (300|350|360)' then 'King Air 300/350' when mf ~ '^KING AIR C90' then 'King Air C90 family'
   when mf ~ '^KING AIR (E90|F90)' then 'King Air E90/F90' when mf ~ '^CARAVAN 208B' then 'Caravan 208B Grand/EX' when mf ~ '^PC-12/4' then 'PC-12 legacy (/45,/47)' when mf ~ '^PC-12 NG' then 'PC-12 NG/NGX'
   when mf ~ '^TBM 700' then 'TBM 700' when mf ~ '^TBM 850' then 'TBM 850' when mf ~ '^TBM (900|910|930|940|960)' then 'TBM 900 family' when mf ~ '^KODIAK' then 'Kodiak 100'
   when mf ~ 'CHEYENNE' then 'Piper Cheyenne' when mf ~ '^CONQUEST I$' then 'Cessna Conquest I' when mf ~ '^CONQUEST II' then 'Cessna Conquest II' when mf ~ '^M-CLASS-TP' then 'Piper Meridian/M500/M600'
   when mf ~ '^(JETPROP|P210 SILVER EAGLE)' or (category='turboprop' and mf ~ 'BO$') then 'EXCLUDE'
   when mf ~ '^(B55|D55|E55|55) BARON' then 'Baron 55 family' when mf ~ '^(58P|58TC) BARON' then 'Baron 58P/58TC' when mf ~ '^58 BARON' then 'Baron 58' when mf ~ '^G58 BARON' then 'Baron G58'
   when mf ~ 'DUKE' then 'Beech Duke' when mf ~ '^(310Q|310R|T310)' then 'Cessna 310' when mf ~ '^340' then 'Cessna 340/340A' when mf ~ '^414' then 'Cessna 414/414A' when mf ~ '^421' then 'Cessna 421B/C'
   when mf ~ '^DA42' then 'Diamond DA42' when mf ~ '^DA62' then 'Diamond DA62' when mf ~ '^SENECA (II|III)$|^SENECA$' then 'Seneca I-III' when mf ~ '^SENECA V' then 'Seneca V'
   when mf ~ '^NAVAJO' then 'Piper Navajo/Chieftain' when mf ~ '^AEROSTAR' then 'Aerostar'
   when mf in ('400','TTX') or mf ~ '^COLUMBIA' then 'Cessna 400/TTx' when mf ~ '^G36' then 'Bonanza G36' when mf ~ '^(206H|TURBO 206H|T206H)' then 'Cessna 206H/T206H'
   when mf ~ '^(182T|TURBO 182T|T182T)' then 'Cessna 182T/T182T' when mf ~ '^(A185F|185F)' then 'Cessna 185' when mf ~ '^M20J' then 'Mooney M20J' when mf ~ '^DA40' then 'Diamond DA40'
   when mf ~ '^SARATOGA' then 'Piper Saratoga' when mf ~ '^HUSKY' then 'Aviat Husky' else initcap(mf) end family from base)
select category, family, count(*) sold, count(distinct year) yrs,
  round(percentile_cont(0.5) within group (order by days_on_market)) med_dom,
  round(avg(red)::numeric,1) avg_cut_pct, round(100.0*avg(case when red>0 then 1 else 0 end),0) cut_rate_pct,
  round((100*regr_slope(ln(last_price), year))::numeric,1) slope_pct_yr, round(percentile_cont(0.5) within group (order by last_price)) med_price
from fam where family<>'EXCLUDE' group by 1,2 having count(*)>=12 and count(distinct year)>=3 order by 1,2;
