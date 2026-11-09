import statistics as st
# (tail, span_days, active_now, first_ask, last_ask or None)
C=[("N1563R",33,0,None,None),("N6736V",28,0,None,None),("N630JL",193,1,319000,304500),("N212TD",193,1,None,None),
("N129BM",178,0,509000,469000),("N36DM",89,0,None,None),("N4203S",177,1,499000,398000),("N25675",20,0,None,None),
("N2024Q",147,0,295000,275000),("N1811Y",174,1,425000,360000),("N48JH",92,0,362000,337000),("N2035R",61,0,None,None),
("N9169Q",92,0,225000,217000),("N72MD",160,1,325000,299000),("N836E",30,0,None,None),("N342S",160,1,205000,195000),
("N903AT",86,0,429000,399000),("N435DG",160,1,579500,539000),("N457DT",159,1,519000,499000),("N3115W",88,0,None,None),
("N6921C",86,0,None,None),("N4260S",50,0,299900,269000),("N8256H",53,0,399000,379000),("N72100",146,1,335000,300000),
("N345CF",38,0,None,None),("N6298X",70,0,359000,279000),("N6755Q",27,0,None,None),("N85BB",130,1,None,None),
("N369SA",130,1,505000,499000),("N709MA",29,0,375000,359000),("N904AD",115,1,279000,269000),("N67551",74,0,None,None),
("N1836B",29,0,None,None),("N117EC",115,1,319500,298500),("N971R",111,1,None,None),("N9099S",107,1,189000,169000),
("N1852S",103,1,None,None),("N711PR",28,0,None,None),("N7936A",27,0,None,None),("N614MM",96,1,310000,229000),
("N22WS",92,1,334000,314900),("N6255J",92,1,459000,439000)]
n=len(C); gone30=[c[0] for c in C if not c[2] and c[1]<=30]; past90=[c[0] for c in C if c[1]>90]
cuts={c[0]:round((c[4]/c[3]-1)*100,2) for c in C if c[3] and c[4]/c[3]-1<=-0.01}
print("cohort",n); print("gone<=30",len(gone30),gone30); print("listed>90",len(past90))
print("cut>=1%",len(cuts),sorted(cuts.items(),key=lambda x:x[1])); print("median cut",st.median([-v for v in cuts.values()]))
ex=[c[0] for c in C if c[0]!="N1811Y"]; print("hero cut",round((360000/425000-1)*100,2))
