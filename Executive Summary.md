---
layout: default
title: Executive Summary
---

# Life Expectancy & Global Health — Executive Summary

A one-page take on the cross-country correlation analysis of life expectancy and 24 WHO health indicators (2015, 183 countries).

> **Interactive version:** [open the dashboard](dashboard.html) for hover details, country-level explorer, and multi-year heatmap. &nbsp;|&nbsp; **Full method & references:** [primary report](Visual%20Data%20Report%20-%20Correlation%20Analysis%20of%20Life%20Expectancy.md) · [follow-up report](Visual%20Data%20Report%20-%20Followup%20Analyses.md).

---

## What the data shows

![Correlation ranking](figures/fig1_correlation_ranking.png)

Nine of 24 indicators cross the strong-correlation threshold (|Pearson r| ≥ 0.70). They split cleanly into two clusters.

| Cluster | Indicator | r | What it measures |
|---|---|---|---|
| **Access to basic services** | UHC service index | **+0.87** | Universal Health Coverage |
| | Basic sanitation | +0.82 | Population with basic sanitation |
| | Basic drinking water | +0.82 | Population with basic drinking water |
| | Clean cooking fuel | +0.79 | Population using clean fuel |
| | Basic handwashing | +0.78 | Households with basic handwashing |
| **Early-life mortality + accidents** | Infant mortality (<1 yr) | **−0.90** | Probability of dying by age 1 |
| | Under-five mortality | −0.87 | Probability of dying by age 5 |
| | Neonatal mortality (<28 d) | −0.87 | Probability of dying in first 28 days |
| | Unintentional poisoning | −0.79 | Poisoning-mortality rate |

**Reading.** Countries with better basic services and lower early-life mortality have systematically higher life expectancy. The size of the early-life-mortality coefficients is mechanically unsurprising — life expectancy at birth integrates over the full age distribution, so child mortality moves it directly.

---

## Three things the follow-up analyses added

**1 · The Pearson screen missed two indicators that matter.**
NTD case counts and nurses-and-midwives density are weak under Pearson but **strong under Spearman** (|ρ| ≈ 0.7). Both distributions are heavily right-skewed; the rank statistic captures monotone relationships that Pearson cannot.

![Pearson vs Spearman](figures/fig2_pearson_vs_spearman.png)

**2 · The strong correlations are stable across 20 years.** Repeating the analysis at 2000, 2010, 2015 (and 2019 where available) shows the same picture, with one notable exception: **unintentional poisoning mortality strengthens** from r = −0.62 in 2000 to −0.79 in 2015.

![Longitudinal heatmap](figures/fig4_longitudinal_heatmap.png)

**3 · Basic handwashing is not just a development proxy.** Controlling for log GDP per capita (PPP), urbanisation, and school life expectancy, handwashing still predicts **+0.126 years of life expectancy per percentage-point** of coverage (SE 0.035, p ≈ 0.001, partial R² = 0.29 on n = 38). A country moving from 30 % to 80 % basic handwashing coverage is predicted to gain ≈ 6.3 years, holding development covariates fixed.

![Handwashing partial regression](figures/fig5_handwash_partial_regression.png)

---

## Bottom line

Among the indicators WHO routinely tracks, **access to basic infrastructure** (water, sanitation, clean fuel, handwashing, UHC) and **child mortality** are the strongest cross-country correlates of life expectancy in 2015. The findings are robust to method, stable across two decades, and — for handwashing specifically — survive the obvious confounder controls. The most useful direction for future work is a confounder-adjusted, longitudinal study of basic handwashing access, which carries unusually high explanatory value per dollar of infrastructure investment.

> **Caveat.** Correlation, not causation. Ecological (country-level) inference does not transfer to individual-level claims. See §4.3 of the [primary report](Visual%20Data%20Report%20-%20Correlation%20Analysis%20of%20Life%20Expectancy.md) for the full limitations list.
