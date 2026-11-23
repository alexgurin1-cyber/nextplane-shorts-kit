"""SR22 G3 (normally aspirated, 2007-2012) N-registered listings seen by NextPlane since tracking began (2026-04-14..2026-11-23),
merged by tail across sources. Pulled from Supabase 2026-11-23 (query in DATA_PACK.md).
Row: tail, year, airframe hrs, first_seen, last_seen, first_ask (jitter-cleaned), current_ask (latest-seen ad), active_now (seen >= 2026-11-19)."""
import statistics as st, datetime as dt
D=lambda s: dt.date.fromisoformat(s)
C=[("N138CK",2009,3100,"2026-10-01","2026-11-23",385000,385000),  # 375K cut reversed in 6 days = noise
("N143E",2012,1455,"2026-04-16","2026-06-02",499900,479900),
("N160PG",2008,1663,"2026-04-18","2026-07-11",365000,365000),  # 145K jitter reversed
("N176CF",2011,1504,"2026-07-17","2026-10-05",485000,485000),
("N1783J",2008,115,"2026-04-18","2026-11-23",494900,494900),
("N197CP",2008,1165,"2026-04-14","2026-05-28",449900,449900),
("N227DZ",2008,1070,"2026-09-25","2026-11-23",444900,444900),
("N22XJ",2012,1530,"2026-11-03","2026-11-23",499900,499900),
("N310JF",2007,1944,"2026-04-20","2026-11-20",363500,310000),
("N314CP",2008,3110,"2026-04-18","2026-06-12",419900,419900),
("N369SF",2008,2417,"2026-04-16","2026-11-23",624900,599900),
("N380SR",2007,1409,"2026-04-14","2026-11-20",369000,325000),  # 125K/120K jitter reversed
("N412CP",2009,3120,"2026-04-16","2026-07-13",429900,429900),  # 200K jitter reversed
("N459J",2007,1370,"2026-05-09","2026-07-13",374900,374900),
("N509CM",2010,1542,"2026-06-04","2026-11-23",485000,465000),
("N554CB",2010,1720,"2026-05-13","2026-09-25",459900,429900),
("N56AH",2007,1875,"2026-07-02","2026-11-23",279073,274680),  # daily FX-style jitter; net -1.6%
("N56PE",2010,1232,"2026-10-23","2026-11-23",465000,465000),
("N618AB",2010,1655,"2026-06-02","2026-11-23",469000,454900),
("N681MB",2010,1593,"2026-04-16","2026-06-02",485900,485900),
("N717AP",2008,2150,"2026-04-16","2026-11-23",459000,439900),
("N725CP",2008,1990,"2026-04-18","2026-11-23",375000,429900),  # relisted 2026-09 at 439,900 after 334,000 -> ambiguous, excluded below
("N747WK",2011,970,"2026-07-15","2026-09-13",510000,510000),
("N766AT",2011,1580,"2026-04-18","2026-05-28",469900,469900),
("N777NL",2007,3111,"2026-11-19","2026-11-23",430000,430000),
("N788PG",2008,2413,"2026-10-29","2026-11-23",440000,430000),
("N809PC",2012,814,"2026-07-07","2026-08-01",489900,489900),
("N814LT",2010,3102,"2026-04-16","2026-11-23",469900,399900),
("N916P",2007,1735,"2026-07-09","2026-08-17",349000,349000),
("N975MS",2008,2800,"2026-09-19","2026-10-17",395000,395000),
("N978SR",2007,1854,"2026-04-16","2026-11-23",349000,299000)]
X={"N725CP":"relisted at a higher price after cuts (ambiguous)","N56AH":"price moves daily with currency conversion (ad priced abroad), not real cuts"}  # N530ET $120,000 placeholder excluded in the query step
c=[r for r in C if r[0] not in X]; n=len(c); print("G3 tails (clean)",n)
TODAY=D("2026-11-23")
act=[r for r in c if D(r[4])>=D("2026-11-19")]; print("active now",len(act))
days={r[0]:(D(r[4])-D(r[3])).days for r in c}
p90=[k for k,v in days.items() if v>90]; print("listed >90 days (so far)",len(p90),round(100*len(p90)/n),"%")
gone30=[r[0] for r in c if r not in act and days[r[0]]<=30]; print("left market within 30 days",len(gone30),gone30)
cut={r[0]:(1-r[6]/r[5])*100 for r in c if r[6]/r[5]<=0.99}; print("cut >=1%",len(cut),round(100*len(cut)/n),"%","typical cut %",round(st.median(cut.values()),1),"typical $",st.median([r[5]-r[6] for r in c if r[0] in cut]))
print("hero cut",round(cut["N814LT"],1),"rank",sorted(cut,key=lambda k:-cut[k]).index("N814LT")+1,"of",len(cut))
print("hero days",days["N814LT"],"rank",sorted(days,key=lambda k:-days[k]).index("N814LT")+1,"of",n)
hi=[r for r in c if r[2]>=2700]; print("high-time G3 (>=2,700 h):",[(r[0],r[1],r[2],r[6]) for r in hi],"asks",min(r[6] for r in hi),max(r[6] for r in hi),"typical",st.median(r[6] for r in hi))
lo=[r for r in act if r[2]<2700]; print("active G3 under 2,700 h typical ask",st.median(r[6] for r in lo),"n",len(lo), "typical hrs", st.median(r[2] for r in lo))
