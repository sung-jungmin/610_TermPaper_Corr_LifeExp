"""
Reproduce the term-paper correlation table from the *current* raw Kaggle CSVs
(WHO World Health Statistics 2020 — utkarshxy/who-worldhealth-statistics-2020-complete).

The Kaggle dataset format changed since 2021 from a pre-cleaned 2-column-per-file
layout to the raw WHO multi-dimensional layout. This script reproduces the
"filtered/cleaned" intermediate used by the original notebook, then recomputes
the pairwise Pearson r between Life Expectancy (2015, both sexes) and the 24
candidate health indicators.
"""

import os
import re
from pathlib import Path
import pandas as pd

PROJ = Path(__file__).parent
RAW = PROJ / "csv_data"
CLEAN = PROJ / "csv_clean"
CLEAN.mkdir(exist_ok=True)

# Maps raw Kaggle filename -> short variable name used by the original notebook.
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

YEAR = 2015
BOTH = {"Both sexes", "Total"}

_NUM = re.compile(r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")

def extract_value(s):
    if pd.isna(s):
        return None
    m = _NUM.match(str(s))
    return float(m.group(1)) if m else None

def clean_one(path: Path, shortname: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["Period"] == YEAR].copy()
    if "Dim1" in df.columns:
        df = df[df["Dim1"].isin(BOTH)].copy()
    df[shortname] = df["First Tooltip"].apply(extract_value)
    out = df[["Location", shortname]].dropna()
    out = out.groupby("Location", as_index=False)[shortname].mean()
    return out

# 1. Build cleaned per-indicator frames.
cleaned: dict[str, pd.DataFrame] = {}
print("Cleaning raw CSVs -> 2015 Both-sexes point estimates")
print(f"{'short name':22s} {'n':>5}  source")
for fname, short in MAPPING.items():
    p = RAW / fname
    if not p.exists():
        print(f"MISSING: {fname}")
        continue
    df = clean_one(p, short)
    cleaned[short] = df
    df.to_csv(CLEAN / fname, index=False)
    print(f"{short:22s} {len(df):>5}  {fname}")

# 2. Pairwise Pearson r vs LifeExp.
LE = cleaned["LifeExp"]
candidates = [s for s in cleaned if s not in ("LifeExp", "HALE")]
results = []
for short in candidates:
    merged = LE.merge(cleaned[short], on="Location", how="inner").dropna()
    n = len(merged)
    r = merged["LifeExp"].corr(merged[short]) if n >= 3 else None
    results.append((short, r, n))

results.sort(key=lambda t: (abs(t[1]) if t[1] is not None else -1), reverse=True)

print("\n=== Pairwise Pearson r vs LifeExp (2015, Both sexes) ===")
print(f"{'rank':>4}  {'variable':22s} {'r':>11} {'n':>5}")
for i, (s, r, n) in enumerate(results, 1):
    rs = f"{r:+.6f}" if r is not None else "n/a"
    print(f"{i:>4}  {s:22s} {rs:>11} {n:>5}")

# 3. Compare to paper numbers.
PAPER = {
    "MR_infant_1y": -0.895958, "MR_infant_5y": -0.874980, "MR_infant_28d": -0.871679,
    "UHC_Cov": 0.865219, "sanitation": 0.822244, "drinking_water": 0.814540,
    "clean_fuel_tech": 0.793851, "MR_Poison": -0.787836, "handwash": 0.782170,
    "safe_san": 0.694502, "doctors": 0.690216, "dentists": 0.684040,
    "Pharmacists": 0.681462, "TB": -0.670218, "cardio_cancer": -0.662305,
    "birth_att_skilled": 0.661455, "Malaria": -0.650912, "HepB": -0.569469,
    "HIV": -0.534991, "alcohol": 0.373452, "Tobacco": 0.265485,
    "nursing_mid": 0.182041, "suicideRate": 0.179331, "NTD": -0.111964,
}
rmap = {s: (r, n) for s, r, n in results}
print("\n=== Recomputed vs paper ===")
print(f"{'variable':22s} {'paper r':>10} {'recomputed':>12} {'delta':>10} {'n':>5}")
max_abs_delta = 0.0
for s, paper_r in PAPER.items():
    r, n = rmap.get(s, (None, 0))
    if r is None:
        print(f"{s:22s}  (missing)")
        continue
    d = r - paper_r
    max_abs_delta = max(max_abs_delta, abs(d))
    print(f"{s:22s} {paper_r:>+10.6f} {r:>+12.6f} {d:>+10.6f} {n:>5}")
print(f"\nMax |delta| across 24 indicators: {max_abs_delta:.6f}")
