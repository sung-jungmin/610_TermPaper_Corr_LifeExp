# Correlation Analysis of Life Expectancy and Global Health Indicators

**A Short Paper Based on WHO World Health Statistics 2020 (Reference Year: 2015)**

| | |
|---|---|
| **Author** | Jungmin Sung |
| **Original project** | DTSC 610 M01 — Term Project, December 15, 2021 |
| **Revised** | May 2026 |

---

## Abstract

Life expectancy at birth is a composite summary of population health, and identifying its strongest cross-country correlates is a useful first step toward causal investigation. This short paper performs a cross-sectional Pearson correlation analysis of life expectancy against 24 health indicators from the WHO *World Health Statistics 2020* dataset, using country-level values for the reference year 2015. Two complementary strategies are compared: (i) **grouped** analysis, in which related indicators are merged on country before computing correlations, and (ii) **pairwise** analysis, in which each indicator is correlated with life expectancy on its own complete-case sample. The pairwise design preserves substantially more observations (up to 183 countries) than the grouped design (as few as 18). At the pre-specified threshold of |r| ≥ 0.70, **nine indicators** show strong correlations: five positive (universal health coverage, basic sanitation, drinking water, clean cooking fuel, basic handwashing facilities) and four negative (neonatal, infant, and under-five mortality; unintentional poisoning mortality). The results motivate three specific follow-up studies, most notably on basic handwashing access — which correlates with life expectancy (r = +0.78) almost as strongly as the Universal Health Coverage index (r = +0.87) despite requiring far less infrastructure investment.

**Keywords:** life expectancy; cross-country correlation; global health indicators; WHO World Health Statistics; SDG-3; Pearson r.

---

## 1. Introduction

Life expectancy at birth integrates a country's age- and cause-specific mortality patterns into a single number and is therefore widely used as a summary indicator of population health. Identifying which observable indicators co-vary most closely with life expectancy is a useful first step in any cause-effect investigation: correlation is not evidence of causation, but it narrows the search space for plausible determinants and prioritizes variables for further mechanistic study (Altman & Krzywinski, 2015).

The WHO *World Health Statistics 2020* report compiles country-level statistics across 39 categories aligned with the Sustainable Development Goals, with particular focus on SDG-3 ("ensure healthy lives and promote well-being for all at all ages") (WHO, 2020). The breadth of this dataset prompts a simple descriptive question: **among the indicators routinely tracked by WHO, which are most tightly coupled to life expectancy at the country level?**

The original goal — fixed at the outset of the project — is to identify indicators whose absolute correlation with life expectancy meets or exceeds **0.70**, a threshold conventionally labelled "strong" on the Evans (1996) scale of correlation magnitude. The intent is not to make causal claims, but to surface a short list of candidate variables that merit follow-up under confounder-adjusted or longitudinal designs.

The contribution of this paper is twofold:

1. A pairwise correlation ranking of 24 health indicators against country-level life expectancy in 2015.
2. A side-by-side comparison of grouped and pairwise analytical strategies, demonstrating that the choice meaningfully changes both sample size and the resulting coefficient estimates.

## 2. Data and Methods

### 2.1 Data source

All data are drawn from the WHO *World Health Statistics 2020* report, accessed via a Kaggle compilation that preserves the original WHO values in a per-indicator CSV layout (Utkarsh, 2020). The full WHO repository is available at <https://www.who.int/data/gho/publications/world-health-statistics>.

### 2.2 Variable selection

After excluding metadata files and indicators without country-level coverage for the chosen reference year, **26 indicator tables** were retained. Each table contains the indicator value for approximately 180 countries across one or more of the years 2000, 2010, 2015, and 2019. **2015** was selected as the reference year because it offers the most complete cross-sectional coverage in the dataset.

The dependent variable is **Life Expectancy at birth (both sexes combined)**. The 24 candidate independent variables span six conceptual categories (Table 1).

**Table 1.** Candidate indicators grouped by conceptual category.

| Category | Indicators (short name) |
|---|---|
| Newborn and child mortality | MR_infant_28d, MR_infant_1y, MR_infant_5y, birth_att_skilled |
| Communicable diseases | Malaria, TB, HepB, NTD, HIV |
| Noncommunicable diseases and mental health | cardio_cancer, suicideRate |
| Health workforce | doctors, nursing_mid, dentists, Pharmacists |
| Water, sanitation and hygiene (WASH) | drinking_water, sanitation, safe_san, handwash |
| Substance use, coverage, environment | alcohol, Tobacco, UHC_Cov, clean_fuel_tech, MR_Poison |

"MR" denotes mortality rate; full WHO definitions are retained as documented in the source data.

### 2.3 Two analytical strategies

**Grouped analysis.** Indicators within a category are inner-joined on country, and the resulting multi-variable dataframe is passed to `pandas.DataFrame.corr()`. This strategy is convenient for visualizing intra-group correlations alongside the correlation with life expectancy, but its sample size is bounded by the country with the **fewest** observations across all merged indicators. For example, the WASH group (drinking water + sanitation + safely managed sanitation + handwashing) reduces to **n = 18 countries** because basic handwashing data is sparsely reported.

**Pairwise (one-by-one) analysis.** Each candidate indicator is inner-joined with life expectancy individually, and correlation is computed on that single complete-case sample. Sample sizes range from 86 (UHC service coverage index) to 183 (cardio_cancer, suicideRate, MR_Poison). This strategy maximizes the number of observations per coefficient and is the primary basis for the strong-correlation ranking reported in Section 3.

### 2.4 Correlation statistic and interpretation

Pearson's product-moment correlation coefficient *r* is used throughout. Coefficient magnitudes are interpreted following Evans (1996):

| \|r\| range | Interpretation |
|---|---|
| 0.90 – 1.00 | Very strong |
| 0.70 – 0.89 | Strong |
| 0.40 – 0.69 | Moderate |
| 0.10 – 0.39 | Weak |
| 0.00 – 0.09 | Negligible |

The pre-specified threshold for the project's primary outcome is **|r| ≥ 0.70**.

### 2.5 Implementation

Analyses were performed in Python 3 using `pandas` for data manipulation and correlation computation, `seaborn` for visualization, and the standard library `glob` / `functools` for file orchestration. The full notebook is preserved alongside this paper as `DTSC610 Term Project - Correlation Analysis of Life Expectancy and Different Variables.ipynb`.

The Kaggle dataset was reformatted between 2021 and 2026 from the pre-cleaned 2-column-per-indicator layout used in the original project to the raw WHO long format (`Location, Period, Indicator, [Dim1], First Tooltip`). A small preprocessing script, `verify_paper.py`, reconstructs the original cleaned tables from the current raw `csv_data/` by filtering `Period == 2015`, restricting `Dim1` to `Both sexes` or `Total` where present, and extracting the point estimate from `First Tooltip` (stripping any bracketed confidence intervals). The reconstructed cleaned tables live in `csv_clean/` and are consumed by the patched notebook.

## 3. Results

### 3.1 Pairwise correlation ranking

Table 2 reports the Pearson correlation between life expectancy and each of the 24 candidate indicators, sorted by |r|.

**Table 2.** Pairwise correlation of life expectancy with 24 health indicators, 2015.

| Rank | Indicator | r | Interpretation | Direction |
|---|---|---|---|---|
| 1 | MR_infant_1y (infant mortality, < 1 yr) | −0.896 | Strong | Negative |
| 2 | MR_infant_5y (under-five mortality) | −0.875 | Strong | Negative |
| 3 | MR_infant_28d (neonatal mortality, < 28 d) | −0.872 | Strong | Negative |
| 4 | UHC_Cov (UHC service coverage index) | +0.865 | Strong | Positive |
| 5 | sanitation (basic sanitation services) | +0.822 | Strong | Positive |
| 6 | drinking_water (basic drinking water services) | +0.815 | Strong | Positive |
| 7 | clean_fuel_tech (reliance on clean cooking fuel) | +0.794 | Strong | Positive |
| 8 | MR_Poison (unintentional poisoning mortality) | −0.788 | Strong | Negative |
| 9 | handwash (basic handwashing at home) | +0.782 | Strong | Positive |
| 10 | safe_san (safely managed sanitation) | +0.695 | Moderate | Positive |
| 11 | doctors (medical doctors per 10,000) | +0.690 | Moderate | Positive |
| 12 | dentists (dentists per 10,000) | +0.684 | Moderate | Positive |
| 13 | Pharmacists (pharmacists per 10,000) | +0.681 | Moderate | Positive |
| 14 | TB (tuberculosis incidence) | −0.670 | Moderate | Negative |
| 15 | cardio_cancer (premature NCD mortality) | −0.662 | Moderate | Negative |
| 16 | birth_att_skilled (skilled birth attendance) | +0.661 | Moderate | Positive |
| 17 | Malaria (malaria incidence) | −0.651 | Moderate | Negative |
| 18 | HepB (HepB surface antigen prevalence) | −0.569 | Moderate | Negative |
| 19 | HIV (HIV incidence) | −0.535 | Moderate | Negative |
| 20 | alcohol (per-capita alcohol consumption) | +0.373 | Weak | Positive |
| 21 | Tobacco (tobacco use prevalence) | +0.265 | Weak | Positive |
| 22 | nursing_mid (nurses and midwives per 10,000) | +0.182 | Weak | Positive |
| 23 | suicideRate (suicide mortality) | +0.179 | Weak | Positive |
| 24 | NTD (neglected tropical disease cases) | −0.112 | Weak | Negative |

### 3.2 Variables crossing the pre-specified |r| ≥ 0.70 threshold

Nine of the 24 indicators meet the pre-specified strong-correlation threshold. They cluster into two thematic groups.

**Positive correlates with life expectancy:**

- Universal Health Coverage service index (r = +0.87)
- Population with basic sanitation services (r = +0.82)
- Population using basic drinking water services (r = +0.82)
- Population with primary reliance on clean fuels and technology (r = +0.79)
- Population with basic handwashing facilities at home (r = +0.78)

**Negative correlates with life expectancy:**

- Infant mortality rate, < 1 year (r = −0.90)
- Under-five mortality rate (r = −0.87)
- Neonatal mortality rate, < 28 days (r = −0.87)
- Unintentional poisoning mortality rate (r = −0.79)

### 3.3 Reproducibility check (2026)

The full analysis was rerun against the current Kaggle dump in May 2026. Twenty-three of the 24 pairwise coefficients in Table 2 match the originally reported values to six decimal places. The single exception is **HIV**, which shifts from −0.534991 to −0.541200 (|Δ| ≈ 0.006), consistent with a small WHO data revision in the new-HIV-infections series. The shift does not change the indicator's interpretation: HIV remains a moderate-band negative correlate, ranked 19th, well below the |r| ≥ 0.70 threshold and outside the strong-correlation cluster. No other indicator's classification (very strong / strong / moderate / weak / negligible) is affected.

### 3.4 Grouped analysis: a cautionary example

For comparison, the grouped analysis of the Communicable Diseases category (n = 86 countries with complete data across Malaria, TB, HepB, NTD, and HIV) yields the following correlations with life expectancy: Malaria −0.63, HepB −0.55, TB −0.52, HIV −0.48, NTD −0.24. The corresponding pairwise coefficients from Section 3.1 are Malaria −0.65, HepB −0.57, TB −0.67, HIV −0.54, NTD −0.11.

The differences are modest for some indicators but substantial for others — TB shifts from −0.52 to −0.67, NTD shifts from −0.24 to −0.11. These shifts reflect both the larger pairwise sample and the changed country composition induced by inner-joining sparse indicators.

## 4. Discussion

### 4.1 Interpretation of the strong correlates

The strong negative correlations between life expectancy and child mortality indicators (|r| ≈ 0.87 – 0.90) are mechanistically unsurprising: deaths in the first five years of life directly lower the life expectancy point estimate, since life expectancy at birth integrates over the full age distribution. The size of the coefficient underscores how much cross-country variation in life expectancy is driven by early-life mortality rather than late-life mortality.

The positive correlations form a coherent cluster around **basic infrastructure and access to services** — clean water, sanitation, handwashing, clean cooking fuel, and health coverage. These indicators all proxy for a country's capacity to deliver basic preventive conditions to its population. The fact that **basic handwashing facilities** (r = +0.78) correlates almost as strongly as the **Universal Health Coverage index** (r = +0.87) is striking: handwashing access requires far less infrastructure investment than a comprehensive health system, yet co-varies with life expectancy at a comparable magnitude. This invites two complementary follow-up questions: (i) is handwashing access functioning as a proxy for broader development, or (ii) does it have independent explanatory power once development confounders are partialled out?

Unintentional poisoning mortality (r = −0.79) deserves brief comment. In the WHO indicator set, poisoning primarily reflects exposure to household chemicals, contaminated food and water, and indoor air pollutants — that is, it is itself partially a downstream consequence of the same WASH and clean-fuel conditions that appear in the positive cluster. This raises a multicollinearity concern that any follow-up multivariate model will need to address.

### 4.2 Why the group-vs-pairwise distinction matters

The original project initially analyzed correlations within thematic groups and then switched to a pairwise design. This was not merely a methodological convenience: as Section 3.4 illustrates, the choice can change correlation estimates by 0.10 – 0.15 in either direction. Two factors drive this:

1. **Sample size.** Grouped analysis loses countries with even a single missing indicator. For the WASH group, this dropped n from a maximum of 162 to 18.
2. **Sample composition.** The countries that survive the inner-join are systematically different — typically wealthier and better-reported — which shifts the correlation toward the variance structure of that selected subsample.

For a descriptive correlation screen — the goal of this paper — the pairwise approach is preferable. Grouped analysis is more appropriate when the substantive question requires conditioning on a specific complete-case cohort, or when intra-group correlations among predictors are themselves of interest.

### 4.3 Limitations

Several limitations should be noted:

- **Cross-sectional, single year.** All correlations reflect 2015 cross-country variation. They cannot speak to within-country trends or lag structures.
- **Ecological design.** Country is the unit of analysis. The findings do not transfer to individual-level inference (the ecological fallacy).
- **No confounder adjustment.** Many of the strong correlates are themselves correlated with national income, urbanization, and education. The pairwise r values reported here are unadjusted.
- **Multiple comparisons.** Twenty-four indicators were screened against a single outcome without formal multiple-comparison correction. The strong-correlation threshold (|r| ≥ 0.70) is large enough that this is unlikely to affect the primary conclusions, but the moderate-band coefficients should be interpreted with caution.
- **Linearity assumption.** Inspection of regression and joint plots for several indicators (e.g., handwashing, alcohol) shows visible heteroscedasticity and possible non-linearity. Spearman rank correlation or non-parametric smoothing would be useful sensitivity checks.

## 5. Conclusion and Future Work

This short paper has revisited a 2021 term project to identify health indicators most strongly correlated with life expectancy at the country level in 2015. Nine indicators meet the pre-specified threshold of |r| ≥ 0.70: five reflect access to basic infrastructure and care (UHC, water, sanitation, clean fuel, handwashing) and four reflect mortality (infant, child, and neonatal mortality, and unintentional poisoning). The pairwise analytical design preserves substantially more observations than the grouped design and yields meaningfully different coefficient estimates for several indicators.

Consistent with the original project's intent, these correlations are framed as a starting point rather than a conclusion. Three concrete extensions are proposed:

1. **Basic handwashing facilities, in depth.** Because handwashing access correlates almost as strongly with life expectancy as UHC despite requiring far less infrastructure, it is a high-leverage candidate for follow-up. A natural next step is a multivariate regression with national income, urbanization, and education as covariates, to test whether handwashing access carries independent explanatory power beyond what these proxies of development already capture.
2. **Longitudinal extension.** Repeating the analysis across 2000, 2010, 2015, and 2019 would clarify whether the strong correlations are stable, strengthening, or weakening over time — particularly important for indicators such as UHC that have been the focus of recent policy attention.
3. **Non-linear sensitivity check.** Re-running the analysis using Spearman rank correlation and locally weighted regression would test the robustness of the rankings to the linearity assumption of Pearson r.

---

## References

Altman, N., & Krzywinski, M. (2015). Association, correlation and causation. *Nature Methods*, 12(10), 899–900.

Evans, J. D. (1996). *Straightforward Statistics for the Behavioral Sciences*. Pacific Grove, CA: Brooks/Cole.

Utkarsh. (2020). *WHO World Health Statistics 2020 — complete* [Data set]. Kaggle. <https://www.kaggle.com/utkarshxy/who-worldhealth-statistics-2020-complete>

World Health Organization. (2020). *World Health Statistics 2020: Monitoring health for the SDGs, Sustainable Development Goals*. Geneva: WHO. <https://www.who.int/data/gho/publications/world-health-statistics>

---

*The original term project was submitted for DTSC 610 M01 on December 15, 2021. This short-paper revision restructures the analysis into a standard scientific paper format, expands the discussion of methodology and limitations, and articulates concrete directions for follow-up study. The reported correlation coefficients are the originals from the December 2021 run; an independent re-execution against the current raw Kaggle CSVs in May 2026 reproduces 23 of the 24 pairwise coefficients to six decimal places — see §3.3 for the single HIV revision.*
