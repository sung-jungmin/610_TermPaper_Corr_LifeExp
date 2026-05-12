"""
Follow-up analyses for the visual data report, §5.
1. Spearman vs Pearson + LOWESS sensitivity for the 9 strong correlates.
2. Longitudinal extension: pairwise r vs LifeExp for 2000, 2010, 2015, 2019.
3. Handwashing multivariate regression with World Bank covariates
   (GDP per capita PPP, urbanization %, secondary-school enrollment).

Writes figures to figures/ and a tab-separated results bundle to
followup_results/ for the companion writeup.
"""

import io
import re
import json
import textwrap
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
from statsmodels.nonparametric.smoothers_lowess import lowess
from statsmodels.graphics.regressionplots import plot_partregress_grid

sns.set_theme(style="whitegrid", context="paper")
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 150
plt.rcParams["axes.titleweight"] = "bold"

PROJ = Path(__file__).parent
RAW = PROJ / "csv_data"
FIG = PROJ / "figures"; FIG.mkdir(exist_ok=True)
OUT = PROJ / "followup_results"; OUT.mkdir(exist_ok=True)

# ---- Shared mapping and preprocessing (mirrors verify_paper.py) ----

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

STRONG = [
    "MR_infant_1y", "MR_infant_5y", "MR_infant_28d", "UHC_Cov", "sanitation",
    "drinking_water", "clean_fuel_tech", "MR_Poison", "handwash",
]
ALL_CANDIDATES = [v for v in MAPPING.values() if v not in ("LifeExp", "HALE")]
FILE_BY_SHORT = {v: k for k, v in MAPPING.items()}

# ============================================================================
# Section 1: Spearman vs Pearson + LOWESS sensitivity (2015 cross-section)
# ============================================================================

print("\n=== Section 1: Spearman vs Pearson (2015) ===")
LE_2015 = load_indicator("lifeExpectancyAtBirth.csv", "LifeExp", 2015)

rows = []
merged_by_var: dict[str, pd.DataFrame] = {}
for short in ALL_CANDIDATES:
    df = load_indicator(FILE_BY_SHORT[short], short, 2015)
    m = LE_2015.merge(df, on="Location", how="inner").dropna()
    merged_by_var[short] = m
    if len(m) < 5:
        continue
    pearson = m["LifeExp"].corr(m[short])
    spearman = m["LifeExp"].corr(m[short], method="spearman")
    rows.append({"variable": short, "n": len(m), "pearson_r": pearson, "spearman_rho": spearman,
                 "delta": spearman - pearson})

sens = pd.DataFrame(rows).sort_values("pearson_r", key=lambda s: s.abs(), ascending=False).reset_index(drop=True)
sens.to_csv(OUT / "section1_pearson_vs_spearman.tsv", sep="\t", index=False, float_format="%.4f")
print(sens.to_string(index=False, float_format="%.4f"))
print(f"\nLargest |Spearman - Pearson| shifts:")
print(sens.reindex(sens["delta"].abs().sort_values(ascending=False).index).head(5)
      [["variable","n","pearson_r","spearman_rho","delta"]].to_string(index=False, float_format="%.4f"))

# --- Figure 1: Bar chart of all 24 pairwise Pearson r ---
fig, ax = plt.subplots(figsize=(7, 8))
order = sens.sort_values("pearson_r")
colors = ["#c0392b" if r < 0 else "#2980b9" for r in order["pearson_r"]]
ax.barh(order["variable"], order["pearson_r"], color=colors, edgecolor="black", linewidth=0.5)
ax.axvline(0, color="black", linewidth=0.7)
for x in (-0.70, -0.40, 0.40, 0.70):
    ax.axvline(x, color="gray", linewidth=0.5, linestyle="--", alpha=0.6)
ax.set_xlabel("Pearson r vs Life Expectancy (2015)")
ax.set_title("Pairwise correlation of 24 health indicators with life expectancy", fontsize=11)
ax.set_xlim(-1, 1)
fig.tight_layout()
fig.savefig(FIG / "fig1_correlation_ranking.png", bbox_inches="tight")
plt.close(fig)

# --- Figure 2: Pearson r vs Spearman rho ---
fig, ax = plt.subplots(figsize=(6.5, 6.5))
ax.plot([-1, 1], [-1, 1], color="gray", linewidth=0.7, linestyle="--", label="y = x")
ax.scatter(sens["pearson_r"], sens["spearman_rho"], s=40, alpha=0.85, color="#2c3e50")
for _, r in sens.iterrows():
    if abs(r["delta"]) > 0.04:
        ax.annotate(r["variable"], (r["pearson_r"], r["spearman_rho"]),
                    xytext=(5, 5), textcoords="offset points", fontsize=8)
ax.set_xlabel("Pearson r")
ax.set_ylabel("Spearman ρ")
ax.set_title("Pearson vs Spearman correlation with life expectancy (24 indicators, 2015)",
             fontsize=10)
ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "fig2_pearson_vs_spearman.png", bbox_inches="tight")
plt.close(fig)

# --- Figure 3: LOWESS for the 9 strong correlates ---
fig, axes = plt.subplots(3, 3, figsize=(11, 10), sharey=False)
for ax, short in zip(axes.flat, STRONG):
    m = merged_by_var[short]
    x = m[short].values; y = m["LifeExp"].values
    ax.scatter(x, y, s=14, alpha=0.6, color="#34495e", edgecolor="none")
    lo = lowess(y, x, frac=0.5, return_sorted=True)
    ax.plot(lo[:, 0], lo[:, 1], color="#e74c3c", linewidth=2)
    pr = m["LifeExp"].corr(m[short])
    sr = m["LifeExp"].corr(m[short], method="spearman")
    ax.set_title(f"{short}  (r={pr:+.2f}, ρ={sr:+.2f}, n={len(m)})", fontsize=9)
    ax.set_xlabel(short, fontsize=8)
    ax.set_ylabel("LifeExp", fontsize=8)
fig.suptitle("LOWESS sensitivity check for the 9 strong correlates (|r| ≥ 0.70)", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(FIG / "fig3_lowess_strong_correlates.png", bbox_inches="tight")
plt.close(fig)

# ============================================================================
# Section 2: Longitudinal extension across 2000, 2010, 2015, 2019
# ============================================================================

print("\n=== Section 2: Longitudinal correlation across years ===")
YEARS = [2000, 2010, 2015, 2019]
long_rows = []
for yr in YEARS:
    le = load_indicator("lifeExpectancyAtBirth.csv", "LifeExp", yr)
    for short in STRONG:
        df = load_indicator(FILE_BY_SHORT[short], short, yr)
        m = le.merge(df, on="Location", how="inner").dropna()
        n = len(m)
        r = m["LifeExp"].corr(m[short]) if n >= 5 else np.nan
        long_rows.append({"year": yr, "variable": short, "n": n, "r": r})

long_df = pd.DataFrame(long_rows)
long_df.to_csv(OUT / "section2_longitudinal.tsv", sep="\t", index=False, float_format="%.4f")
pivot_r = long_df.pivot(index="variable", columns="year", values="r").loc[STRONG]
pivot_n = long_df.pivot(index="variable", columns="year", values="n").loc[STRONG]
print("Pearson r:")
print(pivot_r.to_string(float_format="%.3f"))
print("\nSample size n:")
print(pivot_n.to_string())

# --- Figure 4: Longitudinal heatmap ---
fig, ax = plt.subplots(figsize=(7, 5))
annot = pivot_r.copy().astype(object)
for i in range(pivot_r.shape[0]):
    for j in range(pivot_r.shape[1]):
        v = pivot_r.iat[i, j]
        n = pivot_n.iat[i, j]
        annot.iat[i, j] = f"{v:+.2f}\n(n={int(n)})" if pd.notna(v) else ""
sns.heatmap(pivot_r, annot=annot.values, fmt="", cmap="RdBu_r", center=0, vmin=-1, vmax=1,
            cbar_kws={"label": "Pearson r"}, linewidths=0.5, linecolor="white", ax=ax)
ax.set_title("Pearson r between life expectancy and the 9 strong correlates, by year")
ax.set_xlabel("Reference year")
ax.set_ylabel("Indicator")
fig.tight_layout()
fig.savefig(FIG / "fig4_longitudinal_heatmap.png", bbox_inches="tight")
plt.close(fig)

# ============================================================================
# Section 3: Handwashing multivariate regression with World Bank covariates
# ============================================================================

print("\n=== Section 3: Handwashing multivariate (WB covariates) ===")

WB_INDICATORS = {
    "gdp_pcap": "NY.GDP.PCAP.PP.CD",      # GDP per capita, PPP (current international $)
    "urban_pct": "SP.URB.TOTL.IN.ZS",     # Urban population (% of total)
    "school_yrs": "SE.SCH.LIFE",          # School life expectancy, total (years)
}
WB_YEAR = 2015

def fetch_wb_indicator(code: str, year: int) -> pd.DataFrame:
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
           f"?date={year}&format=json&per_page=400")
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())
    if not isinstance(data, list) or len(data) < 2 or data[1] is None:
        return pd.DataFrame(columns=["wb_name", "value"])
    rows = [{"wb_name": d["country"]["value"], "value": d["value"]}
            for d in data[1] if d.get("value") is not None]
    return pd.DataFrame(rows)

wb = {}
for col, code in WB_INDICATORS.items():
    df = fetch_wb_indicator(code, WB_YEAR)
    wb[col] = df.rename(columns={"value": col})
    print(f"  WB {code} -> {len(df)} non-null observations")

# Country-name harmonization between WHO and WB ----
WHO_TO_WB = {
    "Bolivia (Plurinational State of)": "Bolivia",
    "Czechia": "Czech Republic",
    "Democratic People's Republic of Korea": "Korea, Dem. People's Rep.",
    "Democratic Republic of the Congo": "Congo, Dem. Rep.",
    "Egypt": "Egypt, Arab Rep.",
    "Gambia": "Gambia, The",
    "Iran (Islamic Republic of)": "Iran, Islamic Rep.",
    "Kyrgyzstan": "Kyrgyz Republic",
    "Lao People's Democratic Republic": "Lao PDR",
    "Micronesia (Federated States of)": "Micronesia, Fed. Sts.",
    "Republic of Korea": "Korea, Rep.",
    "Republic of Moldova": "Moldova",
    "Russian Federation": "Russian Federation",
    "Saint Kitts and Nevis": "St. Kitts and Nevis",
    "Saint Lucia": "St. Lucia",
    "Saint Vincent and the Grenadines": "St. Vincent and the Grenadines",
    "Slovakia": "Slovak Republic",
    "Syrian Arab Republic": "Syrian Arab Republic",
    "The former Yugoslav Republic of Macedonia": "North Macedonia",
    "Türkiye": "Turkiye",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "United Republic of Tanzania": "Tanzania",
    "United States of America": "United States",
    "Venezuela (Bolivarian Republic of)": "Venezuela, RB",
    "Viet Nam": "Vietnam",
    "Yemen": "Yemen, Rep.",
}

# Build full 2015 frame for handwash regression
hw_2015 = merged_by_var["handwash"].copy()
hw_2015["wb_name"] = hw_2015["Location"].map(lambda s: WHO_TO_WB.get(s, s))

reg = hw_2015[["Location", "wb_name", "LifeExp", "handwash"]].copy()
for col, df in wb.items():
    reg = reg.merge(df, on="wb_name", how="left")
reg = reg.dropna(subset=["LifeExp", "handwash", "gdp_pcap", "urban_pct", "school_yrs"])
reg["log_gdp"] = np.log(reg["gdp_pcap"])
print(f"\nFinal regression sample: n = {len(reg)} countries")

# Bivariate baseline
X_b = sm.add_constant(reg[["handwash"]])
m_b = sm.OLS(reg["LifeExp"], X_b).fit()

# Full multivariate
X_f = sm.add_constant(reg[["handwash", "log_gdp", "urban_pct", "school_yrs"]])
m_f = sm.OLS(reg["LifeExp"], X_f).fit()

# Save formatted results
with open(OUT / "section3_multivariate.txt", "w", encoding="utf-8") as f:
    f.write("Bivariate: LifeExp ~ handwash\n")
    f.write(str(m_b.summary())); f.write("\n\n")
    f.write("Multivariate: LifeExp ~ handwash + log_gdp + urban_pct + school_yrs\n")
    f.write(str(m_f.summary()))

print("\nBivariate (handwash only):")
print(f"  beta_handwash = {m_b.params['handwash']:+.4f}  SE = {m_b.bse['handwash']:.4f}  "
      f"p = {m_b.pvalues['handwash']:.3g}  R^2 = {m_b.rsquared:.3f}")
print("\nMultivariate (with WB covariates):")
for k in ["handwash", "log_gdp", "urban_pct", "school_yrs"]:
    print(f"  beta_{k:11s} = {m_f.params[k]:+.4f}  SE = {m_f.bse[k]:.4f}  "
          f"p = {m_f.pvalues[k]:.3g}")
print(f"  R^2 (full) = {m_f.rsquared:.3f}")

# Partial r^2 for handwash (full vs reduced without handwash)
X_r = sm.add_constant(reg[["log_gdp", "urban_pct", "school_yrs"]])
m_r = sm.OLS(reg["LifeExp"], X_r).fit()
part_r2 = (m_f.rsquared - m_r.rsquared) / (1 - m_r.rsquared)
print(f"  Partial R^2 of handwash | (log_gdp, urban_pct, school_yrs) = {part_r2:.4f}")

# --- Figure 5: Added-variable plot for handwash ---
fig = plt.figure(figsize=(10, 8))
plot_partregress_grid(m_f, fig=fig)
fig.suptitle("Added-variable (partial regression) plots: LifeExp ~ handwash + log GDP + urban % + school years",
             fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(FIG / "fig5_handwash_partial_regression.png", bbox_inches="tight")
plt.close(fig)

# ============================================================================
# Done.
# ============================================================================

print("\n=== Outputs ===")
print(f"Figures: {FIG}")
for p in sorted(FIG.glob('*.png')):
    print(f"  {p.name}  ({p.stat().st_size//1024} KB)")
print(f"Tables/text: {OUT}")
for p in sorted(OUT.iterdir()):
    print(f"  {p.name}  ({p.stat().st_size//1024} KB)")
