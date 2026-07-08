"""
OEE & Loss-Attribution Dashboard — Streamlit mirror of the standalone HTML.
Same recompute logic (time-weighted, components capped at 100%) so numbers match exactly.
Run:  pip install -r requirements.txt   then   streamlit run app.py
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

HERE = Path(__file__).parent
st.set_page_config(page_title="OEE Dashboard — Cell A01", layout="wide", page_icon="🏭")

BAND_ORDER = [">=80", "50-80", "30-50", "<30"]
BAND_LABEL = {">=80": "≥80 good", "50-80": "50–80 mid", "30-50": "30–50 poor", "<30": "<30 critical"}
BAND_COLOR = {">=80": "#22c98b", "50-80": "#f2b134", "30-50": "#ff8a3d", "<30": "#ff5470"}
COL = {"OEE": "#4da3ff", "A": "#f2b134", "P": "#7c5cff", "Q": "#22c98b"}


@st.cache_data
def load():
    df = pd.read_csv(HERE / "rows_clean.csv")
    df["date"] = pd.to_datetime(df["date"])
    meta = json.loads((HERE / "meta.json").read_text())
    return df, meta


def band_of(oee):
    o = oee * 100
    return ">=80" if o >= 80 else "50-80" if o >= 50 else "30-50" if o >= 30 else "<30"


def aggregate(f: pd.DataFrame) -> dict:
    """Time-weighted OEE with each component capped at 100%. Only valid rows count."""
    v = f[f["valid"] == 1]
    P, R, I = v["planned"].sum(), v["run"].sum(), v["ideal"].sum()
    T, OK = v["total"].sum(), v["ok"].sum()
    A = min(R / P, 1) if P > 0 else 0.0
    Pe = min(I / R, 1) if R > 0 else 0.0
    Q = min(OK / T, 1) if T > 0 else 0.0
    return dict(P=P, R=R, I=I, T=T, OK=OK,
                AL=v["aloss"].sum(), PL=v["ploss"].sum(), QL=v["qloss"].sum(),
                A=A, Pe=Pe, Q=Q, OEE=A * Pe * Q, rows=len(v))


def machine_table(f: pd.DataFrame, cal_days: int) -> pd.DataFrame:
    rows = []
    for m, g in f.groupby("machine"):
        a = aggregate(g)
        rows.append(dict(Machine=m, Type=m[3:5],
                         OEE=round(a["OEE"] * 100, 1), Avail=round(a["A"] * 100, 1),
                         Perf=round(a["Pe"] * 100, 1), Qual=round(a["Q"] * 100, 1),
                         Run_min=round(a["R"]), Planned_min=round(a["P"]),
                         AvailLoss_min=round(a["AL"]), PerfLoss_min=round(a["PL"]),
                         Util=round(a["P"] / (cal_days * 24 * 60) * 100, 1),
                         Band=band_of(a["OEE"]), Records=a["rows"]))
    return pd.DataFrame(rows).sort_values("OEE").reset_index(drop=True)


df, META = load()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Filters")
dmin, dmax = df["date"].min().date(), df["date"].max().date()
dr = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
if isinstance(dr, tuple) and len(dr) == 2:
    d_from, d_to = dr
else:
    d_from = d_to = dr if not isinstance(dr, tuple) else dr[0]

shifts = sorted(df["shift"].unique().tolist())
shift_sel = st.sidebar.selectbox("Shift", ["All"] + shifts)
types = sorted(df["mtype"].unique().tolist())
type_sel = st.sidebar.multiselect("Machine type (line)", types, default=[])
mach_opts = sorted(df["machine"].unique().tolist())
mach_sel = st.sidebar.multiselect("Machine", mach_opts, default=[])
band_sel = st.sidebar.multiselect("OEE band", BAND_ORDER, default=BAND_ORDER,
                                  format_func=lambda b: BAND_LABEL[b])

st.sidebar.caption("World-class OEE ≈ 85% · typical discrete ≈ 60%")

# ---------------- APPLY FILTERS ----------------
mask = (df["date"].dt.date >= d_from) & (df["date"].dt.date <= d_to)
if shift_sel != "All":
    mask &= df["shift"] == shift_sel
if type_sel:
    mask &= df["mtype"].isin(type_sel)
if mach_sel:
    mask &= df["machine"].isin(mach_sel)

# band filter is by each machine's own OEE band across current (pre-band) subset
pre = df[mask]
mband = {m: band_of(aggregate(g)["OEE"]) for m, g in pre.groupby("machine")}
if len(band_sel) < 4:
    keep = {m for m, b in mband.items() if b in band_sel}
    view = pre[pre["machine"].isin(keep)]
else:
    view = pre

cal_days = (pd.Timestamp(d_to) - pd.Timestamp(d_from)).days + 1

# ---------------- HEADER ----------------
st.title("Cell A01 — OEE & Loss Attribution")
st.caption(f"{META['period_start']} → {META['period_end']} · {META['period_days']} calendar days · "
           f"{META['connected']} machines · {META['n_raw']:,} records · **{len(view):,} in current view**")

with st.expander("📌 Assumptions & methodology (every number traces here)", expanded=False):
    st.markdown(f"""
- **Data shape:** pre-aggregated MES/SCADA production-run report — one row per machine × shift × part-run. Durations are given minute columns (no state column → losses arrive pre-bucketed).
- **OEE = A × P × Q.** Availability = Run/Planned (Run = shift-time − availability-loss); Performance = Ideal/Run (Ideal = (Total/parts-per-cycle) × standard-cycle-sec); Quality = OK/Total.
- **Ideal cycle** from the historian's STANDARD_CYCLE_TIME — *measured, not estimated*.
- **Capping:** vendor A/P/Q/OEE columns discarded (they showed Availability −82%, Performance 14,197%). Components recomputed and **capped at 100%** at row level; aggregation is **time-weighted**, not an average of percentages.
- **Quality present** → full OEE (scrap tiny, so Q ≈ 100%). **Shifts** A (day) / B (night, crosses midnight) taken from the SHIFT column.
- **TEEP = OEE × Utilization**, Utilization = Planned ÷ (machines-in-view × days × 24 h).
- **Limits:** no downtime reason codes → no reason-level Pareto, no MTBF/MTTR (only A/P/Q minutes, ranked by machine). Heatmap attributes each shift-length record to its clock-hour (approx). {META['dq_total']:,} rows flagged for data quality.
""")

if len(view) == 0:
    st.warning("No records match the current filters.")
    st.stop()

# ---------------- KPI HEADER ----------------
agg = aggregate(view)
machs = view["machine"].unique().tolist()
per_m = {m: aggregate(view[view["machine"] == m]) for m in machs}
utilized = sum(1 for m in machs if per_m[m]["R"] >= META["shift_min_threshold"])
util_ratio = agg["P"] / (len(machs) * cal_days * 24 * 60) if machs else 0
teep = agg["OEE"] * util_ratio

k = st.columns(6)
k[0].metric("Overall OEE", f"{agg['OEE']*100:.1f}%", help="Full OEE incl. Quality")
k[1].metric("Availability", f"{agg['A']*100:.1f}%", f"{agg['AL']:,.0f} loss min", delta_color="off")
k[2].metric("Performance", f"{agg['Pe']*100:.1f}%", f"{agg['PL']:,.0f} loss min", delta_color="off")
k[3].metric("Quality", f"{agg['Q']*100:.1f}%", f"{agg['T']-agg['OK']:,.0f} bad parts", delta_color="off")
k[4].metric("TEEP", f"{teep*100:.1f}%", f"Util {util_ratio*100:.1f}%", delta_color="off")
k[5].metric("Machines", f"{utilized}/{len(machs)}", "utilized / connected", delta_color="off")

worst = (pd.DataFrame([{"m": m, "OEE": per_m[m]["OEE"], "R": per_m[m]["R"]} for m in machs])
         .query("R >= @META['shift_min_threshold']").nsmallest(5, "OEE"))
st.caption("**Worst-5 (utilized):** " +
           " · ".join(f"{r.m} {r.OEE*100:.1f}%" for r in worst.itertuples()) if len(worst) else "")

st.divider()

# ---------------- TREND + PARETO ----------------
c1, c2 = st.columns([1.6, 1])
with c1:
    st.subheader("OEE trend by day")
    series = st.multiselect("Series", ["OEE", "A", "P", "Q"], default=["OEE", "A", "P", "Q"],
                            format_func=lambda s: {"OEE": "OEE", "A": "Availability", "P": "Performance", "Q": "Quality"}[s],
                            key="trendseries")
    byd = []
    for d, g in view.groupby(view["date"].dt.date):
        a = aggregate(g)
        byd.append(dict(date=d, OEE=a["OEE"]*100, A=a["A"]*100, P=a["Pe"]*100, Q=a["Q"]*100))
    td = pd.DataFrame(byd).sort_values("date")
    fig = go.Figure()
    names = {"OEE": "OEE", "A": "Availability", "P": "Performance", "Q": "Quality"}
    for s in series:
        fig.add_trace(go.Scatter(x=td["date"], y=td[s], name=names[s], mode="lines+markers",
                                 line=dict(color=COL[s], width=2), marker=dict(size=4)))
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(range=[0, 100], title="%"),
                      legend=dict(orientation="h"), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Loss Pareto")
    items = sorted([("Availability loss", agg["AL"], COL["A"]),
                    ("Performance loss", agg["PL"], COL["P"]),
                    ("Quality loss (t-eq)", agg["QL"], COL["Q"])], key=lambda x: x[1], reverse=True)
    tot = sum(i[1] for i in items) or 1
    fig = go.Figure(go.Bar(x=[i[1] for i in items], y=[i[0] for i in items], orientation="h",
                           marker_color=[i[2] for i in items],
                           text=[f"{i[1]/tot*100:.0f}%" for i in items], textposition="auto"))
    fig.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0), template="plotly_white",
                      xaxis_title="lost minutes")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Availability = {items[0][1]/tot*100:.1f}% of all lost minutes · total loss {tot:,.0f} min")

# ---------------- HEATMAP + BANDS ----------------
c3, c4 = st.columns([1.6, 1])
with c3:
    st.subheader("OEE heatmap — hour-of-day × shift")
    hm_shifts = sorted(view["shift"].unique().tolist())
    grid = np.full((len(hm_shifts), 24), np.nan)
    txt = [["" for _ in range(24)] for _ in hm_shifts]
    for si, s in enumerate(hm_shifts):
        for h in range(24):
            g = view[(view["shift"] == s) & (view["hour"] == h)]
            if len(g):
                o = aggregate(g)["OEE"] * 100
                grid[si, h] = o
                txt[si][h] = f"{o:.0f}"
    fig = go.Figure(go.Heatmap(z=grid, x=list(range(24)), y=[f"Shift {s}" for s in hm_shifts],
                               text=txt, texttemplate="%{text}", colorscale=[[0, "#ff5470"], [0.3, "#ff8a3d"],
                               [0.5, "#f2b134"], [0.8, "#22c98b"], [1, "#22c98b"]], zmin=0, zmax=100,
                               colorbar=dict(title="OEE%")))
    fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), template="plotly_white",
                      xaxis_title="hour of day")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Each record spans a full shift; attributed to its clock-hour (approximate).")

with c4:
    st.subheader("Band distribution")
    oee_b = {b: 0 for b in BAND_ORDER}
    ut_b = {b: 0 for b in BAND_ORDER}
    for m in machs:
        a = per_m[m]
        oee_b[band_of(a["OEE"])] += 1
        ut_b[band_of(a["P"] / (cal_days * 24 * 60))] += 1
    bt = st.radio("Band metric", ["OEE band", "Utilization band"], horizontal=True, key="bandmetric")
    src = oee_b if bt == "OEE band" else ut_b
    fig = go.Figure(go.Bar(x=[BAND_LABEL[b] for b in BAND_ORDER], y=[src[b] for b in BAND_ORDER],
                           marker_color=[BAND_COLOR[b] for b in BAND_ORDER],
                           text=[src[b] for b in BAND_ORDER], textposition="auto"))
    fig.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0), template="plotly_white",
                      yaxis_title="machines")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- MACHINE TABLE + DRILL ----------------
st.subheader("Machine table")
mt = machine_table(view, cal_days)
search = st.text_input("Search machine code", "").upper()
show = mt[mt["Machine"].str.contains(search)] if search else mt
st.dataframe(show, use_container_width=True, height=360,
             column_config={"OEE": st.column_config.ProgressColumn("OEE %", min_value=0, max_value=100, format="%.1f"),
                            "Util": st.column_config.NumberColumn("Util %", format="%.1f")})

st.download_button("⭳ Export current view (CSV)", show.to_csv(index=False).encode(),
                   file_name="oee_current_view.csv", mime="text/csv")

st.subheader("🔎 Machine drill-down")
drill = st.selectbox("Pick a machine", ["—"] + mt["Machine"].tolist())
if drill != "—":
    g = view[view["machine"] == drill]
    dcols = st.columns([1.4, 1])
    with dcols[0]:
        byd = []
        for d, gg in g.groupby(g["date"].dt.date):
            a = aggregate(gg)
            byd.append(dict(date=d, OEE=a["OEE"]*100, A=a["A"]*100, P=a["Pe"]*100, Q=a["Q"]*100))
        dd = pd.DataFrame(byd).sort_values("date")
        fig = go.Figure()
        for s in ["OEE", "A", "P", "Q"]:
            fig.add_trace(go.Scatter(x=dd["date"], y=dd[s], name=names[s], mode="lines",
                                     line=dict(color=COL[s], width=2)))
        fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), template="plotly_white",
                          yaxis=dict(range=[0, 100]), title=f"{drill} — daily A/P/Q/OEE")
        st.plotly_chart(fig, use_container_width=True)
    with dcols[1]:
        a = aggregate(g)
        items = sorted([("Availability", a["AL"], COL["A"]), ("Performance", a["PL"], COL["P"]),
                        ("Quality", a["QL"], COL["Q"])], key=lambda x: x[1], reverse=True)
        fig = go.Figure(go.Bar(x=[i[1] for i in items], y=[i[0] for i in items], orientation="h",
                               marker_color=[i[2] for i in items]))
        fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), template="plotly_white",
                          title="Top losses (min)")
        st.plotly_chart(fig, use_container_width=True)

# ---------------- RECONCILIATION + DQ ----------------
c5, c6 = st.columns(2)
with c5:
    st.subheader("Reconciliation check (current view)")
    a = agg
    bal = a["R"] + a["AL"]
    ok = abs(a["P"] - bal) < max(2, a["P"] * 0.001)
    st.markdown(("✅ **Balanced**" if ok else "⚠️ **Gap detected**") + " — Planned = Run + Availability-loss")
    recon = pd.DataFrame([
        ["Planned production time", f"{a['P']:,.0f}", "100%"],
        ["  • Run time", f"{a['R']:,.0f}", f"{a['R']/a['P']*100:.1f}%"],
        ["      – Ideal / productive", f"{a['I']:,.0f}", f"{a['I']/a['P']*100:.1f}%"],
        ["      – Performance loss", f"{a['PL']:,.0f}", f"{a['PL']/a['P']*100:.1f}%"],
        ["  • Availability loss", f"{a['AL']:,.0f}", f"{a['AL']/a['P']*100:.1f}%"],
        ["Run + Availability loss", f"{bal:,.0f}", f"Δ {a['P']-bal:.1f} min"],
    ], columns=["Component", "Minutes", "Share"])
    st.table(recon)
with c6:
    st.subheader("Data quality")
    st.info(f"⚑ {META['dq_total']:,} flagged rows across {META['n_raw']:,} — kept {META['n_kept_valid']:,} valid for metrics")
    dqs = pd.DataFrame([(k, v) for k, v in META["dq_summary"].items()], columns=["Issue", "Rows"]).sort_values("Rows", ascending=False)
    st.table(dqs)
    with st.expander("Sample flagged rows"):
        st.dataframe(pd.DataFrame(META["dq_detail"][:200]), use_container_width=True, height=240)
