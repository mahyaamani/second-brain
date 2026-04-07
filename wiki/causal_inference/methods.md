# Causal Inference — Methods & Research Designs

*Source: Causal Inference: The Mixtape (Cunningham)*

---

## 1. Matching & Subclassification (Ch. 5)

**Goal:** Satisfy the backdoor criterion by comparing treated and control units with similar observable characteristics.

### Subclassification
- Weight differences in means by strata-specific weights
- Adjusts distributions so treatment and control groups are balanced on known confounders
- Originated with Cochran (1968) studying smoking and lung cancer

### Exact Matching
- Match treated units to control units with identical covariate values
- Problem: "curse of dimensionality" — hard to find exact matches with many covariates

### Approximate Matching / Propensity Score
- **Propensity score** = probability of receiving treatment given covariates: P(D=1|X)
- Match on propensity score instead of all covariates (dimension reduction)
- Requires **overlap/common support:** 0 < P(D=1|X) < 1

### Key Assumption: CIA (Selection on Observables)
- All confounders must be observed and controlled for
- Cannot address unobserved confounders

---

## 2. Regression Discontinuity Design — RDD (Ch. 6)

**Core Idea:** Treatment is assigned based on whether a running variable crosses a cutoff. Units just above and just below the cutoff are nearly identical, creating a local quasi-experiment.

### Key Features:
- **Running variable (X):** Continuous score determining treatment
- **Cutoff (c₀):** Threshold above/below which treatment is assigned
- **Sharp RDD:** Treatment deterministically assigned at cutoff
- **Fuzzy RDD:** Cutoff changes probability of treatment (use IV at cutoff)

### Key Assumption: **Continuity**
- Expected potential outcomes are continuous at the cutoff
- No other intervention occurs precisely at the cutoff
- "Nature does not make jumps" (Darwin)

### Estimand:
- **Local ATE** at the cutoff (not generalizable to other points)

### Validity Checks:
- McCrary density test (no bunching/manipulation at cutoff)
- Covariate balance around the cutoff
- Placebo tests at fake cutoffs

### History:
- Invented by Donald Campbell (Thistlethwaite & Campbell, 1960)
- Dormant until 1999 revival by Angrist & Lavy, Black
- Now one of the most popular and credible designs

---

## 3. Instrumental Variables — IV (Ch. 7)

**Core Idea:** Use an external variable (instrument Z) that affects treatment D but has no direct effect on outcome Y except through D.

### Requirements for a Valid Instrument:
1. **Relevance:** Z must be correlated with D (strong first stage)
2. **Exclusion restriction:** Z affects Y only through D (no direct path Z → Y)
3. **Independence:** Z is as good as randomly assigned (or conditionally so)

### Key Estimands:
- **LATE (Local Average Treatment Effect):** Causal effect for "compliers" — units whose treatment status is changed by the instrument
- Compliers, always-takers, never-takers, defiers (monotonicity rules out defiers)

### Estimation:
- **Two-Stage Least Squares (2SLS):**
  1. First stage: Regress D on Z (and controls)
  2. Second stage: Regress Y on predicted D̂ (and controls)
- **Wald estimator:** Simple ratio of reduced-form to first-stage effects

### History:
- Invented by Philip Wright (1928) in a book about tariffs on vegetable oils
- Appendix B contained the first IV proof
- Stock & Trebbi (2003) used stylometric analysis to confirm Philip (not Sewall) as author

---

## 4. Panel Data & Fixed Effects (Ch. 8)

**Core Idea:** Repeatedly observing the same units over time allows you to control for time-invariant unobserved confounders.

### Key Assumptions:
- Confounders are **time-invariant** (fixed over time for each unit)
- No time-varying unobserved confounders correlated with treatment
- No feedback from past outcomes to current treatment

### Estimators:
- **Pooled OLS (POLS):** Ignores panel structure; biased if unobserved heterogeneity exists
- **Fixed Effects (FE):** Includes unit-specific intercepts (or uses within-transformation/demeaning)
  - Eliminates all time-invariant confounders
  - Also eliminates ability to estimate effects of time-invariant variables

### Notation:
Y_it = δD_it + uᵢ + εᵢₜ
- uᵢ = time-invariant unobserved heterogeneity
- εᵢₜ = idiosyncratic (time-varying) error

---

## 5. Difference-in-Differences — DiD (Ch. 9)

**Core Idea:** Compare changes over time between a treated group and a control group. The "difference in differences" removes time-invariant confounders and common time trends.

### Setup:
- Treatment group vs. control group
- Pre-treatment period vs. post-treatment period
- DiD = (Treated_post - Treated_pre) - (Control_post - Control_pre)

### Key Assumption: **Parallel Trends**
- In the absence of treatment, the treated and control groups would have followed the same trend
- Cannot be directly tested (it's about the counterfactual), but can be assessed with pre-treatment data

### Historical Origin:
- **John Snow (1855):** Used DiD logic to prove cholera was waterborne
  - Lambeth water company moved intake upstream (cleaner water) in 1849
  - Southwark & Vauxhall kept intake downstream (contaminated)
  - Compared cholera mortality changes across the two company areas
  - This was ~85 years before the first formal randomized experiment

### Common Applications:
- Policy evaluations (minimum wage, health insurance mandates)
- Natural experiments where treatment timing varies across groups

### Validity Checks:
- Pre-treatment trend analysis (event study plots)
- Placebo tests with fake treatment timing
- Robustness to different control groups

---

## 6. Synthetic Control (Ch. 10)

**Core Idea:** Construct a "synthetic" version of the treated unit by optimally weighting untreated units from a donor pool. The synthetic unit serves as the counterfactual.

### How It Works:
1. Select a **donor pool** of untreated comparison units
2. Choose weights to minimize pre-treatment differences between treated unit and synthetic unit
3. Post-treatment gap = estimated causal effect

### Key Advantages over DiD:
- **No extrapolation:** Uses convex hull (interpolation) of control units
- **Transparent weights:** Explicit about what each unit contributes
- **No peeking:** Design phase doesn't require post-treatment outcome data
- **Single treated unit:** Works well when only one unit is treated (e.g., one state, one country)

### Inference:
- **Permutation/placebo tests:** Apply the method to each untreated unit as if it were treated
- Compare treated unit's gap to distribution of placebo gaps
- If treated unit's gap is extreme → evidence of a treatment effect

### Key Papers:
- Abadie & Gardeazabal (2003) — terrorism and economic activity (Basque Country)
- Abadie, Diamond, & Hainmueller (2010) — California's Proposition 99 (tobacco)
- Athey & Imbens (2017) called it "arguably the most important innovation in policy evaluation in the last 15 years"

### Motivating Example:
- **Card (1990) Mariel Boatlift:** 125,000 Cuban immigrants to Miami in 1980
  - Card found no effect on native wages/employment using ad hoc comparison cities
  - Peri & Yasenov (2018) replicated with synthetic control, found similar results

---

## Method Selection Summary

| Method | Best When | Key Assumption |
|--------|-----------|----------------|
| Matching | All confounders observed | CIA / Selection on observables |
| RDD | Treatment assigned at a cutoff | Continuity at cutoff |
| IV | External instrument available | Exclusion restriction |
| Fixed Effects | Panel data, time-invariant confounders | Strict exogeneity |
| DiD | Natural experiment with treatment/control over time | Parallel trends |
| Synthetic Control | Single treated aggregate unit | Weighted controls reproduce counterfactual |

## See Also

- [causal_inference/overview](causal_inference/overview)
- [causal_inference/key_concepts](causal_inference/key_concepts)
