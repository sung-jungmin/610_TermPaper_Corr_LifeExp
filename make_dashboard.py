"""
Build a single-file interactive Plotly dashboard summarizing the entire analysis.

Outputs dashboard.html in the project root. The file is self-contained — Plotly's
JS is loaded from the CDN — so it works as a GitHub Pages artifact with no build
step.

Six sections:
  1. World map of life expectancy 2015 (choropleth)
  2. Pairwise Pearson correlation ranking (24 indicators)
  3. Country-level explorer (indicator dropdown -> scatter vs LifeExp + LOWESS)
  4. Pearson vs Spearman sensitivity
  5. Longitudinal heatmap (9 strong correlates x 4 years)
  6. Handwashing multivariate (bivariate scatter + WB covariate coefficients)
"""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.io import to_html
import statsmodels.api as sm
from statsmodels.nonparametric.smoothers_lowess import lowess

PROJ = Path(__file__).parent
RAW = PROJ / "csv_data"
OUT = PROJ / "dashboard.html"

# ---- Shared mapping (mirrors verify_paper.py / followup_analyses.py) ----

MAPPING = {
    "30-70cancerChdEtc.csv": "cardio_cancer",
    "alcoholSubstanceAbuse.csv": "alcohol",
    "atLeastBasicSanitizationServices.csv": "sanitation",
    "basicDrinkingWaterServices.csv": "drinking_water",
    "basicHandWashing.csv": "handwash",
    "birthAttendedBySkilledPersonal.csv": "birth_att_skilled",
    "cleanFuelAndTech.csv": "clean_fuel_tech",
    "crudeSuicideRates.csv": "suicideRate",
    "dentists.csv": "dentists",
    "HALElifeExpectancyAtBirth.csv": "HALE",
    "hepatitusBsurfaceAntigen.csv": "HepB",
    "incedenceOfMalaria.csv": "Malaria",
    "incedenceOfTuberculosis.csv": "TB",
    "infantMortalityRate.csv": "MR_infant_1y",
    "interventionAgianstNTDs.csv": "NTD",
    "lifeExpectancyAtBirth.csv": "LifeExp",
    "medicalDoctors.csv": "doctors",
    "mortalityRatePoisoning.csv": "MR_Poison",
    "neonatalMortalityRate.csv": "MR_infant_28d",
    "newHivInfections.csv": "HIV",
    "nursingAndMidwife.csv": "nursing_mid",
    "pharmacists.csv": "Pharmacists",
    "safelySanitization.csv": "safe_san",
    "tobaccoAge15.csv": "Tobacco",
    "uhcCoverage.csv": "UHC_Cov",
    "under5MortalityRate.csv": "MR_infant_5y",
}
BOTH = {"Both sexes", "Total"}
_NUM = re.compile(r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")

# Human-readable label for each short name (for dashboard UI)
LABELS = {
    "LifeExp": "Life expectancy at birth (yr)",
    "MR_infant_1y": "Infant mortality (<1 yr, per 1000)",
    "MR_infant_5y": "Under-five mortality (per 1000)",
    "MR_infant_28d": "Neonatal mortality (<28 d, per 1000)",
    "UHC_Cov": "UHC service coverage index",
    "sanitation": "Basic sanitation services (%)",
    "drinking_water": "Basic drinking water services (%)",
    "clean_fuel_tech": "Clean cooking fuel reliance (%)",
    "MR_Poison": "Unintentional poisoning mortality (per 100k)",
    "handwash": "Basic handwashing at home (%)",
    "safe_san": "Safely managed sanitation (%)",
    "doctors": "Medical doctors (per 10,000)",
    "dentists": "Dentists (per 10,000)",
    "Pharmacists": "Pharmacists (per 10,000)",
    "TB": "Tuberculosis incidence (per 100k)",
    "cardio_cancer": "Premature NCD mortality (%)",
    "birth_att_skilled": "Skilled birth attendance (%)",
    "Malaria": "Malaria incidence (per 1000 at risk)",
    "HepB": "HepB surface antigen prevalence (%)",
    "HIV": "New HIV infections (per 1000 uninfected)",
    "alcohol": "Alcohol consumption (litres/capita)",
    "Tobacco": "Tobacco use prevalence (%)",
    "nursing_mid": "Nurses and midwives (per 10,000)",
    "suicideRate": "Suicide mortality (per 100k)",
    "NTD": "NTD intervention need (people)",
}

# WHO country names -> names plotly's locationmode='country names' recognises
WHO_NAME_MAP = {
    "Bolivia (Plurinational State of)": "Bolivia",
    "Democratic People's Republic of Korea": "North Korea",
    "Democratic Republic of the Congo": "Democratic Republic of the Congo",
    "Iran (Islamic Republic of)": "Iran",
    "Lao People's Democratic Republic": "Laos",
    "Micronesia (Federated States of)": "Micronesia",
    "Republic of Korea": "South Korea",
    "Republic of Moldova": "Moldova",
    "Russian Federation": "Russia",
    "Syrian Arab Republic": "Syria",
    "The former Yugoslav Republic of Macedonia": "North Macedonia",
    "Türkiye": "Turkey",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "United Republic of Tanzania": "Tanzania",
    "United States of America": "United States",
    "Venezuela (Bolivarian Republic of)": "Venezuela",
    "Viet Nam": "Vietnam",
}

def extract_value(s):
    if pd.isna(s):
        return None
    m = _NUM.match(str(s))
    return float(m.group(1)) if m else None

def load_indicator(fname: str, short: str, year: int) -> pd.DataFrame:
    df = pd.read_csv(RAW / fname)
    df = df[df["Period"] == year].copy()
    if "Dim1" in df.columns:
        df = df[df["Dim1"].isin(BOTH)].copy()
    df[short] = df["First Tooltip"].apply(extract_value)
    return df[["Location", short]].dropna().groupby("Location", as_index=False)[short].mean()

# ---- 1. Load all indicators for 2015 ----

print("Loading 2015 data for all 26 indicators...")
data_2015 = {}
for fname, short in MAPPING.items():
    data_2015[short] = load_indicator(fname, short, 2015)
    print(f"  {short:22s} n={len(data_2015[short]):4d}")

LE = data_2015["LifeExp"]
CANDIDATES = [s for s in data_2015 if s not in ("LifeExp", "HALE")]

# ---- Section 1: World map of life expectancy 2015 ----

print("\nBuilding Section 1: Choropleth")
map_df = LE.copy()
map_df["plotly_name"] = map_df["Location"].map(lambda s: WHO_NAME_MAP.get(s, s))
fig_map = px.choropleth(
    map_df, locations="plotly_name", locationmode="country names",
    color="LifeExp", hover_name="Location",
    color_continuous_scale="Viridis", range_color=[50, 85],
    labels={"LifeExp": "Life expectancy (yr)"},
)
fig_map.update_layout(
    template="plotly_white",
    margin=dict(l=0, r=0, t=10, b=0),
    height=460,
    geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
)

# ---- Section 2: Pearson correlation ranking ----

print("Building Section 2: Correlation ranking")
rows = []
for short in CANDIDATES:
    m = LE.merge(data_2015[short], on="Location", how="inner").dropna()
    if len(m) < 5:
        continue
    pr = m["LifeExp"].corr(m[short])
    sr = m["LifeExp"].corr(m[short], method="spearman")
    rows.append({"variable": short, "label": LABELS[short], "n": len(m),
                 "pearson": pr, "spearman": sr})
sens = pd.DataFrame(rows).sort_values("pearson")
colors_bar = ["#c0392b" if r < 0 else "#2980b9" for r in sens["pearson"]]
fig_rank = go.Figure(go.Bar(
    x=sens["pearson"], y=sens["variable"], orientation="h",
    marker=dict(color=colors_bar, line=dict(color="black", width=0.5)),
    customdata=np.stack([sens["label"], sens["n"], sens["spearman"]], axis=-1),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Pearson r: %{x:+.3f}<br>"
        "Spearman ρ: %{customdata[2]:+.3f}<br>"
        "n: %{customdata[1]} countries<extra></extra>"
    ),
))
for x in (-0.70, -0.40, 0.40, 0.70):
    fig_rank.add_vline(x=x, line=dict(color="gray", width=0.6, dash="dash"))
fig_rank.add_vline(x=0, line=dict(color="black", width=0.8))
fig_rank.update_layout(
    template="plotly_white",
    margin=dict(l=140, r=20, t=10, b=40),
    xaxis_title="Pearson r vs Life Expectancy (2015)",
    xaxis=dict(range=[-1, 1]),
    height=620,
)

# ---- Section 3: Country-level explorer (dropdown of indicators) ----

print("Building Section 3: Country-level explorer")
strong_first = ["UHC_Cov", "handwash", "sanitation", "drinking_water", "clean_fuel_tech",
                "MR_infant_1y", "MR_infant_5y", "MR_infant_28d", "MR_Poison"]
ordered = strong_first + [s for s in CANDIDATES if s not in strong_first]

traces, lowess_traces, buttons = [], [], []
for i, short in enumerate(ordered):
    m = LE.merge(data_2015[short], on="Location", how="inner").dropna().reset_index(drop=True)
    visible = (i == 0)
    # Scatter
    traces.append(go.Scatter(
        x=m[short], y=m["LifeExp"], mode="markers", name="countries",
        marker=dict(size=8, color="#2c3e50", opacity=0.7,
                    line=dict(color="white", width=0.5)),
        text=m["Location"],
        hovertemplate=("<b>%{text}</b><br>" + short + ": %{x:.2f}<br>"
                       "Life expectancy: %{y:.2f} yr<extra></extra>"),
        visible=visible,
    ))
    # LOWESS
    if len(m) >= 8:
        lo = lowess(m["LifeExp"].values, m[short].values, frac=0.5, return_sorted=True)
        lowess_traces.append(go.Scatter(
            x=lo[:, 0], y=lo[:, 1], mode="lines", name="LOWESS",
            line=dict(color="#e74c3c", width=3),
            hoverinfo="skip", visible=visible,
        ))
    else:
        lowess_traces.append(go.Scatter(x=[], y=[], mode="lines", visible=visible))
    pr = m["LifeExp"].corr(m[short]) if len(m) >= 3 else float("nan")
    sr = m["LifeExp"].corr(m[short], method="spearman") if len(m) >= 3 else float("nan")
    button_title = (f"<b>{LABELS[short]}</b> &nbsp;·&nbsp; "
                    f"Pearson r = {pr:+.3f}, Spearman ρ = {sr:+.3f}, n = {len(m)}")
    vis = [False] * (len(ordered) * 2)
    vis[i] = True; vis[i + len(ordered)] = True
    buttons.append(dict(
        label=f"{short} — {LABELS[short]}",
        method="update",
        args=[{"visible": vis},
              {"title": button_title,
               "xaxis": {"title": LABELS[short]}}],
    ))

fig_explorer = go.Figure(data=traces + lowess_traces)
pr0 = LE.merge(data_2015[ordered[0]], on="Location").dropna()
pr0_r = pr0["LifeExp"].corr(pr0[ordered[0]])
pr0_s = pr0["LifeExp"].corr(pr0[ordered[0]], method="spearman")
fig_explorer.update_layout(
    template="plotly_white",
    title=(f"<b>{LABELS[ordered[0]]}</b> &nbsp;·&nbsp; "
           f"Pearson r = {pr0_r:+.3f}, Spearman ρ = {pr0_s:+.3f}, n = {len(pr0)}"),
    xaxis_title=LABELS[ordered[0]],
    yaxis_title="Life expectancy at birth (yr)",
    height=520,
    margin=dict(l=60, r=20, t=70, b=50),
    showlegend=False,
    updatemenus=[dict(
        buttons=buttons,
        direction="down", x=0, xanchor="left", y=1.15, yanchor="top",
        bgcolor="white", bordercolor="#aaa",
    )],
)

# ---- Section 4: Pearson vs Spearman ----

print("Building Section 4: Pearson vs Spearman")
fig_ps = go.Figure()
fig_ps.add_trace(go.Scatter(
    x=[-1, 1], y=[-1, 1], mode="lines", name="y = x",
    line=dict(color="gray", dash="dash", width=1),
    hoverinfo="skip",
))
sens["delta_abs"] = (sens["spearman"] - sens["pearson"]).abs()
fig_ps.add_trace(go.Scatter(
    x=sens["pearson"], y=sens["spearman"], mode="markers+text",
    name="indicators",
    marker=dict(size=10, color="#34495e", opacity=0.85,
                line=dict(color="white", width=0.5)),
    text=[v if d > 0.04 else "" for v, d in zip(sens["variable"], sens["delta_abs"])],
    textposition="top center", textfont=dict(size=10),
    customdata=np.stack([sens["label"], sens["n"], sens["spearman"] - sens["pearson"]], axis=-1),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Pearson r: %{x:+.3f}<br>"
        "Spearman ρ: %{y:+.3f}<br>"
        "Δ (ρ − r): %{customdata[2]:+.3f}<br>"
        "n: %{customdata[1]} countries<extra></extra>"
    ),
))
fig_ps.update_layout(
    template="plotly_white",
    xaxis=dict(title="Pearson r", range=[-1, 1]),
    yaxis=dict(title="Spearman ρ", range=[-1, 1]),
    height=540, margin=dict(l=60, r=20, t=10, b=50),
    showlegend=False,
)

# ---- Section 5: Longitudinal heatmap ----

print("Building Section 5: Longitudinal heatmap")
YEARS = [2000, 2010, 2015, 2019]
STRONG = ["MR_infant_1y", "MR_infant_5y", "MR_infant_28d", "UHC_Cov", "sanitation",
          "drinking_water", "clean_fuel_tech", "MR_Poison", "handwash"]
long_r = pd.DataFrame(index=STRONG, columns=YEARS, dtype=float)
long_n = pd.DataFrame(index=STRONG, columns=YEARS, dtype=int)
for yr in YEARS:
    le_y = load_indicator("lifeExpectancyAtBirth.csv", "LifeExp", yr)
    for short in STRONG:
        df = load_indicator({v: k for k, v in MAPPING.items()}[short], short, yr)
        m = le_y.merge(df, on="Location", how="inner").dropna()
        long_n.at[short, yr] = len(m)
        long_r.at[short, yr] = m["LifeExp"].corr(m[short]) if len(m) >= 5 else np.nan

text = [[f"{long_r.iat[i,j]:+.2f}<br>n={int(long_n.iat[i,j])}" if not pd.isna(long_r.iat[i,j]) else "—"
         for j in range(len(YEARS))] for i in range(len(STRONG))]
fig_long = go.Figure(go.Heatmap(
    z=long_r.values, x=[str(y) for y in YEARS], y=STRONG,
    colorscale="RdBu_r", zmid=0, zmin=-1, zmax=1,
    text=text, texttemplate="%{text}",
    hovertemplate="<b>%{y}</b> in %{x}<br>Pearson r: %{z:+.3f}<extra></extra>",
    colorbar=dict(title="Pearson r"),
))
fig_long.update_layout(
    template="plotly_white",
    xaxis_title="Reference year",
    yaxis_title="Indicator",
    height=460, margin=dict(l=140, r=20, t=10, b=50),
    yaxis=dict(autorange="reversed"),
)

# ---- Section 6: Handwashing multivariate ----

print("Building Section 6: Handwashing multivariate (using cached followup data)")
# Re-fetch WB covariates and rerun handwash regression (same as followup_analyses.py)
import urllib.request, json as jsonlib

WB_INDICATORS = {
    "gdp_pcap":   "NY.GDP.PCAP.PP.CD",
    "urban_pct":  "SP.URB.TOTL.IN.ZS",
    "school_yrs": "SE.SCH.LIFE",
}
def fetch_wb_indicator(code, year=2015):
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
           f"?date={year}&format=json&per_page=400")
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = jsonlib.loads(resp.read())
    if not isinstance(data, list) or len(data) < 2 or data[1] is None:
        return pd.DataFrame(columns=["wb_name", "value"])
    rows = [{"wb_name": d["country"]["value"], "value": d["value"]}
            for d in data[1] if d.get("value") is not None]
    return pd.DataFrame(rows)
WB_NAME_MAP = {
    "Bolivia (Plurinational State of)": "Bolivia",
    "Czechia": "Czech Republic", "Egypt": "Egypt, Arab Rep.",
    "Iran (Islamic Republic of)": "Iran, Islamic Rep.",
    "Kyrgyzstan": "Kyrgyz Republic",
    "Lao People's Democratic Republic": "Lao PDR",
    "Republic of Korea": "Korea, Rep.",
    "Republic of Moldova": "Moldova",
    "Slovakia": "Slovak Republic",
    "Türkiye": "Turkiye",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "United Republic of Tanzania": "Tanzania",
    "United States of America": "United States",
    "Venezuela (Bolivarian Republic of)": "Venezuela, RB",
    "Viet Nam": "Vietnam",
    "Yemen": "Yemen, Rep.",
    "Democratic Republic of the Congo": "Congo, Dem. Rep.",
}
hw = LE.merge(data_2015["handwash"], on="Location").dropna()
hw["wb_name"] = hw["Location"].map(lambda s: WB_NAME_MAP.get(s, s))
for col, code in WB_INDICATORS.items():
    wb_df = fetch_wb_indicator(code).rename(columns={"value": col})
    hw = hw.merge(wb_df, on="wb_name", how="left")
hw = hw.dropna(subset=["LifeExp", "handwash", "gdp_pcap", "urban_pct", "school_yrs"])
hw["log_gdp"] = np.log(hw["gdp_pcap"])
X = sm.add_constant(hw[["handwash", "log_gdp", "urban_pct", "school_yrs"]])
mfit = sm.OLS(hw["LifeExp"], X).fit()

# Bivariate scatter with both bivariate and multivariate fit lines
xs = np.linspace(hw["handwash"].min(), hw["handwash"].max(), 50)
biv = sm.OLS(hw["LifeExp"], sm.add_constant(hw[["handwash"]])).fit()
y_biv = biv.params["const"] + biv.params["handwash"] * xs
mean_other = hw[["log_gdp", "urban_pct", "school_yrs"]].mean()
y_mv = (mfit.params["const"] + mfit.params["handwash"] * xs +
        mfit.params["log_gdp"] * mean_other["log_gdp"] +
        mfit.params["urban_pct"] * mean_other["urban_pct"] +
        mfit.params["school_yrs"] * mean_other["school_yrs"])

fig_hw = go.Figure()
fig_hw.add_trace(go.Scatter(
    x=hw["handwash"], y=hw["LifeExp"], mode="markers",
    name=f"countries (n = {len(hw)})",
    marker=dict(size=10, color=hw["gdp_pcap"], colorscale="Viridis",
                colorbar=dict(title="GDP per cap<br>(PPP $)"),
                line=dict(color="white", width=0.5)),
    text=hw["Location"],
    hovertemplate=("<b>%{text}</b><br>"
                   "Handwashing: %{x:.1f} %<br>"
                   "Life expectancy: %{y:.2f} yr<br>"
                   "GDP per cap: $%{marker.color:,.0f}<extra></extra>"),
))
fig_hw.add_trace(go.Scatter(
    x=xs, y=y_biv, mode="lines",
    name=f"bivariate β = {biv.params['handwash']:+.3f}",
    line=dict(color="#e74c3c", width=2.5),
    hoverinfo="skip",
))
fig_hw.add_trace(go.Scatter(
    x=xs, y=y_mv, mode="lines",
    name=f"multivariate β = {mfit.params['handwash']:+.3f} (controls held at sample mean)",
    line=dict(color="#27ae60", width=2.5, dash="dot"),
    hoverinfo="skip",
))
fig_hw.update_layout(
    template="plotly_white",
    xaxis_title="Population with basic handwashing facilities at home (%)",
    yaxis_title="Life expectancy at birth (yr)",
    height=520, margin=dict(l=60, r=20, t=10, b=50),
    legend=dict(yanchor="bottom", y=0.02, xanchor="right", x=0.98,
                bgcolor="rgba(255,255,255,0.85)"),
)

# ---- HTML assembly ----

print("\nAssembling dashboard.html...")

def chart_div(fig, div_id, include_js=False):
    return to_html(fig, include_plotlyjs=("cdn" if include_js else False),
                   full_html=False, div_id=div_id, config={"displaylogo": False})

section1 = chart_div(fig_map,      "chart-map",      include_js=True)
section2 = chart_div(fig_rank,     "chart-rank")
section3 = chart_div(fig_explorer, "chart-explorer")
section4 = chart_div(fig_ps,       "chart-ps")
section5 = chart_div(fig_long,     "chart-long")
section6 = chart_div(fig_hw,       "chart-hw")

CSS = """
<style>
  :root { --txt:#222; --muted:#666; --line:#e1e4e8; --accent:#2980b9; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         color: var(--txt); max-width: 1180px; margin: 0 auto; padding: 24px;
         line-height: 1.55; }
  header { border-bottom: 1px solid var(--line); padding-bottom: 16px; margin-bottom: 24px; }
  h1 { margin: 0 0 6px; font-size: 28px; }
  .sub { color: var(--muted); font-size: 14px; }
  nav { position: sticky; top: 0; z-index: 10; background: rgba(255,255,255,0.95);
        backdrop-filter: blur(6px); padding: 10px 0; border-bottom: 1px solid var(--line);
        margin-bottom: 24px; font-size: 14px; }
  nav a { color: var(--accent); text-decoration: none; margin-right: 14px; }
  nav a:hover { text-decoration: underline; }
  section { margin: 36px 0; }
  section h2 { font-size: 20px; margin: 0 0 4px; }
  section .lead { color: var(--muted); font-size: 14px; margin: 0 0 14px; }
  .footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line);
            color: var(--muted); font-size: 13px; }
  .footer a { color: var(--accent); }
  .pill { display:inline-block; padding: 2px 8px; border-radius: 10px;
          background: #eef3f8; color: #2c5b86; font-size: 12px; margin-right: 6px; }
</style>
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Life Expectancy &amp; Global Health — Interactive Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
{CSS}
</head>
<body>
<header>
  <h1>Life Expectancy &amp; Global Health</h1>
  <div class="sub">
    Interactive dashboard accompanying the
    <a href="Visual%20Data%20Report%20-%20Correlation%20Analysis%20of%20Life%20Expectancy.md">primary visual data report</a>
    and its <a href="Visual%20Data%20Report%20-%20Followup%20Analyses.md">follow-up analyses</a>.
    Cross-country correlation analysis of 24 WHO health indicators against
    country-level life expectancy in 2015.
  </div>
  <div style="margin-top:8px">
    <span class="pill">WHO World Health Statistics 2020</span>
    <span class="pill">183 countries</span>
    <span class="pill">24 health indicators</span>
    <span class="pill">2015 reference year</span>
  </div>
</header>

<nav>
  <a href="#map">🌍 World map</a>
  <a href="#rank">📊 Correlation ranking</a>
  <a href="#explore">🔎 Country explorer</a>
  <a href="#sens">🧪 Pearson vs Spearman</a>
  <a href="#long">⏱ Longitudinal</a>
  <a href="#hw">🚿 Handwashing</a>
</nav>

<section id="map">
  <h2>1 · Life expectancy across the world (2015)</h2>
  <p class="lead">Choropleth of life expectancy at birth in 2015. Hover for the country value.</p>
  {section1}
</section>

<section id="rank">
  <h2>2 · Which indicators correlate most strongly with life expectancy?</h2>
  <p class="lead">Pairwise Pearson r between life expectancy and each of 24 health indicators in 2015,
     sorted by sign and magnitude. Dashed lines mark the |r| = 0.40 and 0.70 strength thresholds.
     Nine indicators cross the |r| ≥ 0.70 cutoff.</p>
  {section2}
</section>

<section id="explore">
  <h2>3 · Country-level explorer</h2>
  <p class="lead">Pick an indicator from the dropdown to see country-level scatter against life expectancy
     plus a LOWESS smoother. Hover any point for the country name and exact values.
     Indicators in the dropdown are ordered with the nine strong correlates first.</p>
  {section3}
</section>

<section id="sens">
  <h2>4 · Robustness — Pearson vs Spearman</h2>
  <p class="lead">Each indicator's Pearson r (linear) plotted against its Spearman ρ (rank). Points on
     the y = x diagonal are robust to the choice of statistic. Points well above or below the diagonal
     are sensitive to non-linearity — notable examples flagged with their labels.</p>
  {section4}
</section>

<section id="long">
  <h2>5 · Are the strong correlations stable over time?</h2>
  <p class="lead">Pearson r between life expectancy and each strong correlate at four reference years
     (2000, 2010, 2015, 2019). Hover a cell for the exact coefficient. Empty cells mean the indicator
     is not reported in the Kaggle dump for that year.</p>
  {section5}
</section>

<section id="hw">
  <h2>6 · Handwashing — proxy or independent predictor?</h2>
  <p class="lead">Country-level scatter of life expectancy against basic handwashing access,
     colour-coded by GDP per capita (PPP). Red line: bivariate fit. Green dotted line:
     multivariate fit holding log GDP, urbanisation, and school life expectancy at the sample mean.
     The slope barely halves under controls — handwashing carries independent explanatory power
     beyond development proxies.</p>
  {section6}
</section>

<div class="footer">
  Source: WHO <a href="https://www.who.int/data/gho/publications/world-health-statistics">World Health Statistics 2020</a>
  via the Kaggle compilation <code>utkarshxy/who-worldhealth-statistics-2020-complete</code>;
  World Bank Indicators API for GDP / urbanisation / education in §6.
  Generated by <code>make_dashboard.py</code>. ·
  <a href="README.md">Repository README</a>
</div>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
size_kb = OUT.stat().st_size / 1024
print(f"\nWrote {OUT.name} ({size_kb:.0f} KB)")
