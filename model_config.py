# Single source of truth for assumptions (used by Excel builder AND Streamlit app)
COMPANY = {
    "name": "Isarwerk Präzision GmbH",
    "tagline": "Precision metal & plastic components for automotive and industrial customers",
    "revenue_m": 320, "employees": 1100, "plants": "3 plants (Bavaria, Saxony, Czechia)",
    "suppliers": 1800, "erp": "SAP S/4HANA",
}
TYPES = ["Direct material & components (PO)", "Indirect purchases & services (PO)", "Freight & logistics", "Utilities, rent, fees (no PO)"]
SHORT = ["Direct material", "Indirect & services", "Freight", "No-PO costs"]
SPEND_SHARE = [0.50, 0.10, 0.03, 0.04]
AVG_VALUE = [6500, 2000, 800, 1600]
MANUAL_MIN = [10, 11, 8, 15]
SCEN = ["Conservative", "Base", "Optimistic"]
ZT = {  # share handled end-to-end without a person
    "Conservative": [0.60, 0.50, 0.55, 0.30],
    "Base":         [0.75, 0.65, 0.70, 0.45],
    "Optimistic":   [0.85, 0.75, 0.80, 0.55],
}
RES_MIN = {  # minutes a person still spends on an invoice that needs one
    "Conservative": [6, 6, 5, 10],
    "Base":         [5, 5, 4, 8],
    "Optimistic":   [4.5, 4.5, 3.5, 7],
}
MON_MIN = 0.25
CASH_SHARE = {"Conservative": 0.40, "Base": 0.60, "Optimistic": 0.80}
LABOUR_RATE = 45.00
PROD_HOURS = 1540
PLATFORM_PER_INV = 1.00
IMPLEMENTATION = 50000
SKONTO_SHARE = 0.20
SKONTO_PCT = 0.02
CAPTURE_TODAY = 0.15
CAPTURE_BLP = {"Conservative": 0.35, "Base": 0.50, "Optimistic": 0.75}

def volumes(revenue_m):
    spend = [revenue_m*1e6*s for s in SPEND_SHARE]
    cnt = [round(sp/v, -2) for sp, v in zip(spend, AVG_VALUE)]
    return spend, cnt

def run(scen, revenue_m=None, cnt=None, zt=None, res=None, labour=None, prod=None,
        cash=None, plat=None, impl=None, manual=None):
    revenue_m = revenue_m or COMPANY["revenue_m"]
    spend, c0 = volumes(revenue_m)
    cnt = cnt or c0
    zt = zt or ZT[scen]; res = res or RES_MIN[scen]
    labour = LABOUR_RATE if labour is None else labour
    prod = prod or PROD_HOURS
    cash = CASH_SHARE[scen] if cash is None else cash
    plat = PLATFORM_PER_INV if plat is None else plat
    impl = IMPLEMENTATION if impl is None else impl
    manual = manual or MANUAL_MIN
    tot = sum(cnt)
    h_today_t = [n*m/60 for n, m in zip(cnt, manual)]
    auto = [n*z for n, z in zip(cnt, zt)]
    person = [n-a for n, a in zip(cnt, auto)]
    h_new_t = [(a*MON_MIN + p*r)/60 for a, p, r in zip(auto, person, res)]
    h0, h1 = sum(h_today_t), sum(h_new_t)
    saved = h0-h1
    cap = saved*labour
    cashv = cap*cash
    platform = tot*plat
    net = cashv-platform
    sk = (spend[0]+spend[1])*SKONTO_SHARE*SKONTO_PCT*(CAPTURE_BLP[scen]-CAPTURE_TODAY)
    return dict(scen=scen, cnt=cnt, spend=spend, total=tot, auto=auto, person=person,
        auto_total=sum(auto), person_total=sum(person), auto_share=sum(auto)/tot,
        h_today_t=h_today_t, h_new_t=h_new_t, h0=h0, h1=h1, saved=saved, red=saved/h0,
        fte0=h0/prod, fte1=h1/prod, fte_freed=saved/prod, capacity_value=cap, cash_value=cashv,
        platform=platform, net=net, year1=net-impl, impl=impl,
        payback=(impl/net*12 if net > 0 else None), breakeven=cashv, breakeven_per_inv=cashv/tot,
        skonto=sk, total_incl=net+sk, inv_per_fte0=tot/(h0/prod), inv_per_fte1=tot/(h1/prod))

if __name__ == "__main__":
    for s in SCEN:
        r = run(s)
        print(s, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items() if k in
              ("total","auto_share","h0","h1","saved","fte0","fte1","fte_freed","capacity_value","cash_value","platform","net","year1","payback","skonto","inv_per_fte0","inv_per_fte1")})
