import os
import altair as alt
import pandas as pd
import streamlit as st
from model_config import (COMPANY, TYPES, SHORT, SCEN, ZT, RES_MIN, MANUAL_MIN, LABOUR_RATE, PROD_HOURS,
                          PLATFORM_PER_INV, IMPLEMENTATION, CASH_SHARE, volumes, run)

st.set_page_config(page_title="What is BLP worth to us?", page_icon="📄", layout="wide")

def eur(x): return f"€{x:,.0f}"
def k(x): return f"€{x/1000:,.0f}k"

AUTO_C, PERSON_C, TODAY_C = "#2E8B7A", "#F2A154", "#9AA9B8"

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("Try your own numbers")
    scen = st.radio("How optimistic should we be?", SCEN, index=1,
                    help="Conservative = what independent benchmarks support. Base = close to BLP's own claim. Optimistic = BLP at its best.")
    revenue = st.slider("Annual revenue (€ million)", 50, 1000, COMPANY["revenue_m"], 10)
    _, default_cnt = volumes(revenue)
    st.caption("Invoices per year, by type (estimated from revenue — overwrite with your real counts)")
    cnt = [st.number_input(SHORT[i], min_value=0, value=int(default_cnt[i]), step=500, key=f"cnt{i}_{revenue}") for i in range(4)]
    with st.expander("More assumptions"):
        labour = st.number_input("Cost of one hour of AP work (€)", 10.0, 200.0, LABOUR_RATE, 1.0)
        prod = st.number_input("Working hours per person per year", 800, 2200, PROD_HOURS, 20)
        cash = st.slider("Share of saved time that turns into real cash", 0, 100, int(CASH_SHARE[scen]*100), 5, key=f"cash_{scen}",
                         help="Saved hours only become cash if you avoid a hire, overtime or temps, or move people to other work.") / 100
        plat = st.number_input("BLP fee per invoice (€) — placeholder", 0.0, 20.0, PLATFORM_PER_INV, 0.1,
                               help="BLP does not publish prices. Replace with a real quote.")
        impl = st.number_input("One-time setup cost (€) — placeholder", 0, 1_000_000, IMPLEMENTATION, 5000)
        st.caption("Share of invoices BLP handles without a person")
        zt = [st.slider(SHORT[i], 0, 100, int(ZT[scen][i]*100), 5, key=f"zt{i}_{scen}")/100 for i in range(4)]
        st.caption("Minutes a person still needs on invoices that are not automatic")
        res = [st.number_input(SHORT[i], 0.5, 30.0, float(RES_MIN[scen][i]), 0.5, key=f"res{i}_{scen}") for i in range(4)]
        st.caption("Minutes of AP work per invoice today")
        manual = [st.number_input(SHORT[i], 1.0, 60.0, float(MANUAL_MIN[i]), 0.5, key=f"man{i}") for i in range(4)]

common = dict(revenue_m=revenue, cnt=cnt, labour=labour, prod=prod, plat=plat, impl=impl, manual=manual)
r = run(scen, zt=zt, res=res, cash=cash, **common)
all_r = {s: (r if s == scen else run(s, **common)) for s in SCEN}

# ------------------------------------------------------------------ header
st.title(f"What would BLP be worth to {COMPANY['name']}?")
st.caption("A fictional company, built only from public information. Change any number on the left — everything updates.")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue", f"€{revenue:,.0f}M")
c2.metric("Employees", f"{COMPANY['employees']:,}" if revenue == COMPANY["revenue_m"] else "—")
c3.metric("Supplier invoices / year", f"{r['total']:,.0f}")
c4.metric("People handling them today", f"{r['fte0']:.1f}")
c5.metric("ERP", COMPANY["erp"])
st.markdown(f"**{COMPANY['name']}** — {COMPANY['tagline'].lower()}; {COMPANY['plants']}. Invoices arrive by email, PDF, EDI and paper from about {COMPANY['suppliers']:,} suppliers.")

st.divider()

# ------------------------------------------------------------------ the answer
st.subheader("The answer in one line")
if r["net"] > 0:
    st.success(f"**{scen} case: about {eur(r['net'])} a year after paying BLP, and the investment pays back in "
               f"{r['payback']:.1f} months.** BLP could charge up to {eur(r['breakeven'])} a year (≈ €{r['breakeven_per_inv']:.2f} per invoice) before it stops paying off.")
else:
    st.error(f"**{scen} case: with these inputs BLP does not pay for itself.** It would need to cost less than {eur(r['breakeven'])} a year "
             f"(≈ €{r['breakeven_per_inv']:.2f} per invoice).")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Hours saved per year", f"{r['saved']:,.0f}", f"{r['red']*100:.0f}% less invoice work")
m2.metric("Team capacity freed", f"{r['fte_freed']:.1f} people", f"of {r['fte0']:.1f} today", delta_color="off")
m3.metric("Cash-relevant saving / year", eur(r["cash_value"]), f"{cash*100:.0f}% of {eur(r['capacity_value'])} time value", delta_color="off")
m4.metric("Net value after BLP fee", eur(r["net"]), f"year 1: {eur(r['year1'])} after setup", delta_color="off")

# ------------------------------------------------------------------ process visual
st.subheader("How BLP handles your invoices")
st.markdown(f"""
<style>
.flow{{display:flex;gap:6px;align-items:stretch;margin:6px 0 14px 0}}
.step{{flex:1;background:#F2F6FA;border-radius:12px;padding:12px 12px;border:1px solid #DCE6F0}}
.step b{{display:block;color:#1F6FB5;margin-bottom:3px}}
.step span{{font-size:0.85rem;color:#4A5A6A}}
.arrow{{align-self:center;color:#9AA9B8;font-size:1.4rem}}
.big{{border-radius:12px;padding:14px 16px;border:1px solid #DCE6F0}}
.big h2{{margin:0;font-size:2rem}}
</style>
<div class="flow">
<div class="step"><b>1 · Invoice arrives</b><span>Email, PDF, EDI or paper</span></div><div class="arrow">→</div>
<div class="step"><b>2 · BLP reads it</b><span>Every line, any layout</span></div><div class="arrow">→</div>
<div class="step"><b>3 · Checks against SAP</b><span>Order, goods receipt and price</span></div><div class="arrow">→</div>
<div class="step"><b>4 · Fixes small differences</b><span>Within your own rules</span></div><div class="arrow">→</div>
<div class="step"><b>5 · Posts to SAP</b><span>With a full audit trail</span></div>
</div>
<div style="display:flex;gap:12px">
<div class="big" style="flex:1;background:#EAF4F2"><span>Invoices per year</span><h2>{r['total']:,.0f}</h2></div>
<div class="big" style="flex:1;background:#EAF4F2"><span>Handled start to finish by BLP</span><h2 style="color:{AUTO_C}">{r['auto_total']:,.0f} <small>({r['auto_share']*100:.0f}%)</small></h2></div>
<div class="big" style="flex:1;background:#FEF3E6"><span>Need a person (mostly one-click approval)</span><h2 style="color:#C9791F">{r['person_total']:,.0f} <small>({(1-r['auto_share'])*100:.0f}%)</small></h2></div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2)
df1 = pd.DataFrame({"Invoice type": SHORT * 2,
                    "Group": ["Handled by BLP"]*4 + ["Needs a person"]*4,
                    "Invoices": r["auto"] + r["person"]})
ch1 = (alt.Chart(df1).mark_bar().encode(
    y=alt.Y("Invoice type:N", sort=SHORT, title=None),
    x=alt.X("Invoices:Q", stack="zero", title="Invoices per year"),
    color=alt.Color("Group:N", scale=alt.Scale(domain=["Handled by BLP", "Needs a person"], range=[AUTO_C, PERSON_C]), legend=alt.Legend(orient="bottom", title=None)),
    tooltip=["Invoice type", "Group", alt.Tooltip("Invoices:Q", format=",.0f")]).properties(height=240, title="Which invoices BLP can finish on its own"))
left.altair_chart(ch1, width="stretch")

df2 = pd.DataFrame({"Invoice type": SHORT * 2, "When": ["Today"]*4 + ["With BLP"]*4, "Hours": r["h_today_t"] + r["h_new_t"]})
ch2 = (alt.Chart(df2).mark_bar().encode(
    y=alt.Y("Invoice type:N", sort=SHORT, title=None),
    yOffset="When:N",
    x=alt.X("Hours:Q", title="Hours of AP work per year"),
    color=alt.Color("When:N", scale=alt.Scale(domain=["Today", "With BLP"], range=[TODAY_C, AUTO_C]), legend=alt.Legend(orient="bottom", title=None)),
    tooltip=["Invoice type", "When", alt.Tooltip("Hours:Q", format=",.0f")]).properties(height=240, title="Hours of work: today vs with BLP"))
right.altair_chart(ch2, width="stretch")

# ------------------------------------------------------------------ numbers table
st.subheader("The numbers, three ways")
rows = [
    ("Invoices BLP handles on its own", lambda x: f"{x['auto_share']*100:.0f}%"),
    ("Hours saved per year", lambda x: f"{x['saved']:,.0f}"),
    ("Team capacity freed (people)", lambda x: f"{x['fte_freed']:.1f}"),
    ("Value of the saved time", lambda x: eur(x["capacity_value"])),
    ("…of which real cash", lambda x: eur(x["cash_value"])),
    ("BLP fee (placeholder)", lambda x: eur(x["platform"])),
    ("Net value per year", lambda x: eur(x["net"])),
    ("Payback on setup cost (months)", lambda x: f"{x['payback']:.1f}" if x["payback"] else "n/a"),
    ("Most BLP could cost per year and still break even", lambda x: eur(x["breakeven"])),
    ("Extra, not counted above: early-payment discounts", lambda x: eur(x["skonto"])),
]
tbl = pd.DataFrame({s + (" ◀ selected" if s == scen else ""): [f(all_r[s]) for _, f in rows] for s in SCEN}, index=[n for n, _ in rows])
st.dataframe(tbl, width="stretch")
st.caption("The selected case uses your sidebar changes; the other two use standard assumptions with your revenue, invoice counts and cost inputs.")

# ------------------------------------------------------------------ honesty
st.subheader("What to keep in mind")
st.markdown(f"""
- **Saved time is not automatically cash.** The cash figure assumes {cash*100:.0f}% of freed hours turn into avoided hires, less overtime or temps, or people moved to other work.
- **BLP's price is a placeholder** (€{plat:.2f} per invoice + {eur(impl)} setup) because BLP does not publish prices. The break-even line shows the most it could cost.
- **The share of invoices BLP handles alone is the biggest unknown.** BLP says about 70%; independent studies show about 50% for the best teams. Try Conservative to see the safe case.
- Early-payment discounts could add up to {k(r['skonto'])} a year but depend on supplier terms and cash, so they are kept out of the main number.
""")
xlsx = os.path.join(os.path.dirname(__file__), "Isarwerk_AP_Value_Model.xlsx")
if os.path.exists(xlsx):
    with open(xlsx, "rb") as f:
        st.download_button("Download every assumption, rationale and source (Excel)", f, file_name="Isarwerk_AP_Value_Model.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.caption("Fictional company. Built from public information only (blp.digital, Destatis, ZVEI, IDC, APQC, Ardent Partners). Calculations are plain arithmetic — no AI is used to produce the numbers.")
