# Follow-up Analyses to "Correlation Analysis of Life Expectancy and Global Health Indicators"

**Companion to the primary visual data report, addressing the three follow-up studies proposed in §5.**

| | |
|---|---|
| **Author** | Jungmin Sung |
| **Primary report** | [Visual Data Report - Correlation Analysis of Life Expectancy.md](Visual%20Data%20Report%20-%20Correlation%20Analysis%20of%20Life%20Expectancy.md) |
| **Date** | May 2026 |

---

## Abstract

This companion report implements the three follow-up studies proposed in §5 of the primary visual data report. (i) A Spearman / LOWESS sensitivity check confirms that the nine strong Pearson correlates (|r| ≥ 0.70) are robust to the linearity assumption, but flags two indicators — neglected tropical diseases (NTD) and nurses-and-midwives density — whose rank correlations with life expectancy are an order of magnitude larger than their Pearson counterparts, indicating substantial non-linearity that the original screen missed. (ii) Repeating the pairwise correlation analysis at four reference years (2000, 2010, 2015, 2019) shows that the strong correlates are temporally stable, with one indicator — unintentional poisoning mortality — strengthening materially over time (r = −0.62 in 2000 → r = −0.79 in 2015). Longitudinal coverage is limited for several indicators (UHC, handwashing, and other WASH measures lack 2019 data in the dump). (iii) Regressing life expectancy on basic handwashing access while controlling for log GDP per capita (PPP), urbanization, and school life expectancy yields β_handwash = +0.126 years per percentage-point (SE = 0.035, p ≈ 0.001) on the n = 38 country sample with complete covariates. Handwashing's partial R² conditional on the development covariates is 0.286, supporting the primary report's conjecture that basic handwashing carries independent explanatory power beyond what national-development proxies already capture.

**Keywords:** Spearman correlation; LOWESS; longitudinal correlation; partial regression; World Bank Indicators; sensitivity analysis.

---

## 1. Sensitivity to the Pearson linearity assumption

### 1.1 Method

For each of the 24 candidate indicators, both Pearson r and Spearman ρ were computed against country-level life expectancy in 2015. For the 9 strong correlates (|r| ≥ 0.70), LOWESS smoothers (`statsmodels.nonparametric.smoothers_lowess`, frac = 0.5) were overlaid on the bivariate scatter to inspect non-linearity.

### 1.2 Results

The strong correlates are robust to the choice of statistic. All nine retain |ρ| ≥ 0.79 and shift by at most ±0.04 between Pearson and Spearman; no indicator crosses the strength-tier boundary (Table 1, top block). LOWESS curves for the nine strong correlates are visually monotone (Figure 3); the largest visible curvature is in the handwashing scatter, but the Pearson and Spearman coefficients agree (+0.78 vs +0.79).

**Table 1.** Pearson r and Spearman ρ for the 24 indicators, 2015. Rows sorted by |r|.

| Variable | n | Pearson r | Spearman ρ | ρ − r |
|---|---|---|---|---|
| MR_infant_1y | 162 | −0.896 | −0.919 | −0.022 |
| MR_infant_5y | 162 | −0.875 | −0.920 | −0.044 |
| MR_infant_28d | 182 | −0.872 | −0.885 | −0.014 |
| UHC_Cov | 183 | +0.865 | +0.883 | +0.018 |
| sanitation | 183 | +0.822 | +0.827 | +0.005 |
| drinking_water | 183 | +0.815 | +0.834 | +0.020 |
| clean_fuel_tech | 179 | +0.794 | +0.797 | +0.003 |
| MR_Poison | 183 | −0.788 | −0.812 | −0.024 |
| handwash | 89 | +0.782 | +0.789 | +0.007 |
| safe_san | 84 | +0.695 | +0.689 | −0.006 |
| doctors | 102 | +0.690 | +0.722 | +0.032 |
| dentists | 84 | +0.684 | +0.672 | −0.012 |
| Pharmacists | 79 | +0.681 | +0.758 | +0.076 |
| TB | 183 | −0.670 | −0.784 | −0.113 |
| cardio_cancer | 183 | −0.662 | −0.717 | −0.055 |
| birth_att_skilled | 90 | +0.661 | +0.385 | **−0.276** |
| Malaria | 107 | −0.651 | −0.742 | −0.091 |
| HepB | 183 | −0.569 | −0.665 | −0.095 |
| HIV | 116 | −0.541 | −0.608 | −0.067 |
| alcohol | 182 | +0.373 | +0.397 | +0.023 |
| Tobacco | 144 | +0.265 | +0.291 | +0.025 |
| nursing_mid | 128 | +0.182 | +0.721 | **+0.539** |
| suicideRate | 183 | +0.179 | +0.223 | +0.044 |
| NTD | 183 | −0.112 | −0.687 | **−0.575** |

The far more interesting findings sit in the moderate-to-weak band, where three indicators show |ρ − r| > 0.20:

- **NTD (neglected tropical disease cases)**: Pearson r = −0.11 (negligible) but Spearman ρ = −0.69 (moderate, near strong). NTD case counts are highly skewed — a handful of countries report counts in the tens of millions — so the rank correlation captures a monotone relationship that the Pearson coefficient cannot. The primary report screened NTD out at |r| = 0.11; under a rank statistic, NTD is comparable to TB or HepB in strength.
- **Nurses and midwives per 10,000 (`nursing_mid`)**: Pearson r = +0.18 (weak) vs Spearman ρ = +0.72 (strong). Same diagnosis: extreme right-skew in the workforce density distribution (most countries < 50, a few > 200 per 10,000) compresses the Pearson correlation.
- **Skilled birth attendance (`birth_att_skilled`)**: r = +0.66 vs ρ = +0.39 — the only indicator where Spearman is smaller than Pearson by more than 0.05. The relationship has a ceiling at 100%, with many countries clustered near it; Pearson treats the linear stretch from 50–100% as more informative than its rank order does.

### 1.3 Interpretation

The Pearson screen used in the primary report is well-suited to the strong-correlate cluster — all nine strong indicators are also strong under Spearman, and LOWESS confirms monotonicity. However, the weak-band ranking should not be taken at face value: NTD and nursing-and-midwife density would both be candidates for follow-up if the screen were repeated with a rank statistic. This is consistent with the primary report's stated limitation in §4.3 ("Pearson assumes linearity") and concretizes its practical consequence.

**Figures.** [`figures/fig1_correlation_ranking.png`](figures/fig1_correlation_ranking.png) (bar chart of all 24 Pearson coefficients), [`figures/fig2_pearson_vs_spearman.png`](figures/fig2_pearson_vs_spearman.png) (scatter of Pearson r vs Spearman ρ), [`figures/fig3_lowess_strong_correlates.png`](figures/fig3_lowess_strong_correlates.png) (3 × 3 LOWESS grid for the strong correlates).

---

## 2. Longitudinal stability across reference years

### 2.1 Method

The pairwise correlation between life expectancy and each of the nine strong correlates was recomputed for four reference years: 2000, 2010, 2015, and 2019. Each cell of the resulting table is an independent Pearson r on the country sample with non-missing values for life expectancy and the indicator in that year.

### 2.2 Results

**Table 2.** Pearson r between life expectancy and the 9 strong correlates, by year. Sample sizes in parentheses. NaN indicates that the indicator has no observations for that year in the current Kaggle dump.

| Variable | 2000 | 2010 | 2015 | 2019 |
|---|---|---|---|---|
| MR_infant_1y | −0.901 (161) | −0.886 (162) | −0.896 (162) | −0.892 (162) |
| MR_infant_5y | −0.904 (161) | −0.895 (162) | −0.875 (162) | −0.870 (162) |
| MR_infant_28d | −0.824 (182) | −0.828 (182) | −0.872 (182) | −0.876 (182) |
| UHC_Cov | — | — | +0.865 (183) | — |
| sanitation | +0.835 (175) | +0.824 (182) | +0.822 (183) | — |
| drinking_water | +0.800 (177) | +0.810 (182) | +0.815 (183) | — |
| clean_fuel_tech | +0.813 (179) | +0.788 (179) | +0.794 (179) | — |
| MR_Poison | −0.623 (183) | −0.772 (183) | −0.788 (183) | — |
| handwash | +0.839 (9) | +0.762 (65) | +0.782 (89) | — |

Three patterns stand out:

1. **Infant/child mortality coefficients are essentially flat** across two decades. The under-five mortality coefficient drifts from −0.90 to −0.87, the infant mortality coefficient from −0.90 to −0.89. As discussed in the primary report §4.1, this is mechanically expected: cross-country variation in life expectancy continues to be dominated by early-life mortality.
2. **Neonatal mortality strengthens** (r = −0.82 in 2000 → −0.88 in 2015–2019). One plausible reading: as the gap in post-neonatal mortality narrows globally, the surviving cross-country variation in life expectancy concentrates more in the first 28 days of life.
3. **Unintentional poisoning mortality strengthens markedly**: r = −0.62 in 2000 → −0.77 in 2010 → −0.79 in 2015. The relationship became stronger over the period, possibly because countries that successfully reduced poisoning mortality were also the same countries that gained the most life-expectancy years.

The four WASH-style indicators (sanitation, drinking water, clean fuel, handwashing) are missing 2019 values in the Kaggle dump, and several indicators have severely sparse early-year coverage — handwashing has n = 9 in 2000, which is too few for a reliable coefficient. UHC_Cov has only 2015 (and 2017, unused here) in this dataset and cannot be tracked longitudinally.

### 2.3 Interpretation

For indicators with stable longitudinal coverage, the original cross-sectional finding is not a 2015 artifact: the strong correlations persist across multiple two-decade snapshots. The data limitations of the dump (incomplete 2019 coverage for WASH and UHC indicators) are not analyst-correctable without going back to the WHO source.

**Figure.** [`figures/fig4_longitudinal_heatmap.png`](figures/fig4_longitudinal_heatmap.png).

---

## 3. Handwashing access after controlling for development covariates

### 3.1 Motivation

The primary report observed that handwashing access (r = +0.78) correlates almost as strongly with life expectancy as the Universal Health Coverage index (r = +0.87), despite requiring far less infrastructure. It asked: does handwashing access have independent explanatory power, or is it acting as a proxy for broader national development? The natural test is to regress life expectancy on handwashing access while controlling for indicators of development.

### 3.2 Data and method

Three covariates were drawn from the World Bank Indicators API (accessed May 2026):

- `log_gdp` — natural log of GDP per capita, PPP, current international $ (`NY.GDP.PCAP.PP.CD`)
- `urban_pct` — urban population as percentage of total (`SP.URB.TOTL.IN.ZS`)
- `school_yrs` — school life expectancy in years (`SE.SCH.LIFE`)

All covariates are for 2015 and were inner-joined to the WHO life-expectancy + handwashing 2015 frame after harmonizing country names (e.g., "Iran (Islamic Republic of)" → "Iran, Islamic Rep."). The complete-case regression sample has **n = 38 countries**, limited primarily by `SE.SCH.LIFE` coverage.

Two OLS models were fit:

- **Bivariate:** LifeExp ~ const + handwash
- **Multivariate:** LifeExp ~ const + handwash + log_gdp + urban_pct + school_yrs

### 3.3 Results

**Table 3.** OLS coefficient estimates. Standard errors in parentheses.

| Term | Bivariate β (SE) | Multivariate β (SE) |
|---|---|---|
| Intercept | 50.95 (1.73), p < 10⁻¹⁹ | 41.49 (15.94), p = 0.014 |
| handwash | **+0.175 (0.022), p = 2 × 10⁻⁹** | **+0.126 (0.035), p = 9 × 10⁻⁴** |
| log_gdp | — | +0.44 (1.52), p = 0.78 |
| urban_pct | — | +0.056 (0.052), p = 0.28 |
| school_yrs | — | +0.52 (0.40), p = 0.20 |
| R² | 0.633 | 0.701 |

The bivariate slope is +0.175 years of life expectancy per percentage-point of population with basic handwashing access — meaningful and tightly estimated. In the multivariate model, the handwashing slope attenuates to +0.126 but **remains highly significant (p ≈ 0.001)**. None of the three development covariates is individually significant in the n = 38 sample; the multicollinearity between log_gdp, urban_pct, and school_yrs (pairwise correlations all > 0.6 in this sample) inflates their standard errors and is the likely cause.

The partial R² of handwashing conditional on the development covariates is

$$R^2_{\text{partial}} = \frac{R^2_{\text{full}} - R^2_{\text{reduced}}}{1 - R^2_{\text{reduced}}} = \frac{0.701 - 0.581}{1 - 0.581} = 0.286$$

That is, **handwashing access explains roughly 29 % of the residual life-expectancy variance that the three development proxies leave unexplained.** This addresses the question posed by the primary report directly: handwashing is not merely a development proxy in this sample.

### 3.4 Caveats

- The sample is small (n = 38) because the intersection of WHO handwashing data, WB school life expectancy, and the other indicators is sparse for 2015. A more carefully assembled sample (e.g., imputing one missing covariate or using a different education metric like `SE.SEC.ENRR`) could double n.
- The non-significance of the development covariates does not imply they don't matter — they are tightly correlated with each other and with handwashing, which spreads the explanatory weight across collinear predictors.
- The regression is still cross-sectional and ecological. The §4.3 limitations of the primary report (no causal claim, country-level inference only) carry over.

### 3.5 Interpretation

Subject to the small-sample caveat, this is the strongest evidence the dataset can offer for the primary report's central conjecture: **basic handwashing access is associated with life expectancy beyond what is explained by national income, urbanization, and educational attainment**. The 0.126 year-per-percentage-point estimate also has a useful unit interpretation: a country moving from 30 % to 80 % basic handwashing coverage is predicted to gain ≈ 6.3 years of life expectancy, holding development covariates fixed.

**Figure.** [`figures/fig5_handwash_partial_regression.png`](figures/fig5_handwash_partial_regression.png).

---

## 4. Summary

| Follow-up | Finding | Strength |
|---|---|---|
| §1 Spearman / LOWESS | 9 strong correlates robust; **NTD and nursing-midwife density are strong rank-correlates that the Pearson screen missed** | High — large sample, clear pattern |
| §2 Longitudinal (2000–2019) | Strong correlates are temporally stable. **Unintentional poisoning mortality strengthens markedly (−0.62 → −0.79).** WASH/UHC coverage missing in 2019 dump | Medium — limited by data coverage |
| §3 Handwashing multivariate | **β_handwash = +0.126 years/percentage-point survives WB controls (p ≈ 0.001, partial R² = 0.29)** | Medium — small n (38), but effect is significant |

All three follow-ups support the primary report's headline finding: **basic infrastructure and access indicators (UHC, WASH, clean fuel) are the strongest cross-country correlates of life expectancy in 2015**, and basic handwashing access in particular is not merely a development proxy. The most consequential surprise is §1's discovery that NTD and nursing-and-midwife density carry meaningful information that the Pearson screen suppressed — a worthwhile direction for any future analysis that re-screens the dataset with a rank statistic.

---

## How to reproduce

```bash
# 1. Re-download the raw Kaggle CSVs (already in csv_data/)
# 2. Re-derive cleaned 2015 tables and verify Pearson r against the report
python verify_paper.py

# 3. Run all three follow-up analyses; produces figures/ and followup_results/
python followup_analyses.py
```

Required packages: `pandas`, `numpy`, `seaborn`, `matplotlib`, `statsmodels`, `scipy`.

The World Bank covariate fetch in §3 calls the public `api.worldbank.org` Indicators API and requires network access; no credentials are needed.

---

## References

The references for the primary report apply. Additional methods references:

Cleveland, W. S. (1979). Robust locally weighted regression and smoothing scatterplots. *Journal of the American Statistical Association*, 74(368), 829–836.

World Bank. (n.d.). *World Bank Open Data* [Data set]. <https://data.worldbank.org/>. Indicator codes used: NY.GDP.PCAP.PP.CD, SP.URB.TOTL.IN.ZS, SE.SCH.LIFE.
