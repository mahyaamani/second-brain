# Causal Inference: The Mixtape — Overview

**Author:** Scott Cunningham (Baylor University)
**URL:** https://mixtape.scunning.com/
**Format:** Free online textbook (also available in print)
**Languages:** Code examples in R, Stata, and Python

## What Is Causal Inference?

Causal inference is the leveraging of theory and deep knowledge of institutional details to estimate the impact of events and choices on a given outcome of interest. It encompasses the tools that allow social scientists to determine **what causes what** in a messy, non-experimental world.

**Examples of causal questions:**
- Impact of minimum wage increases on employment
- Effects of early childhood education on incarceration
- Influence of malaria nets on economic growth in developing regions

## Book Structure

The book is organized into 10 chapters covering foundational theory and the major quasi-experimental research designs:

| Ch | Topic | Key Idea |
|----|-------|----------|
| 1 | Introduction | Author's path; what is causal inference |
| 2 | Probability & Regression | Foundational stats: probability, OLS, conditional expectations |
| 3 | Directed Acyclical Graphs (DAGs) | Graphical causal models, backdoor criterion, collider bias |
| 4 | Potential Outcomes Model | Rubin causal model, counterfactuals, ATE, SUTVA |
| 5 | Matching & Subclassification | CIA, exact/approximate matching, propensity scores |
| 6 | Regression Discontinuity Design (RDD) | Cutoff-based treatment, continuity assumption, sharp vs fuzzy |
| 7 | Instrumental Variables (IV) | Exclusion restriction, LATE, 2SLS, history of IV |
| 8 | Panel Data | Fixed effects, pooled OLS, time-invariant confounders |
| 9 | Difference-in-Differences (DiD) | Parallel trends, natural experiments, two-way FE |
| 10 | Synthetic Control | Weighted counterfactual, donor pool, permutation inference |

## Key Intellectual Foundations

- **Rubin Causal Model (Potential Outcomes):** Causal effects defined as comparison between factual and counterfactual states
- **Judea Pearl (DAGs):** Graphical notation for causal relationships; backdoor criterion
- **Credibility Revolution:** Movement in economics led by Angrist, Card, Krueger, Levitt emphasizing research design over structural models
- **Historical roots:** Fisher (1935) randomization, Haavelmo (1943), Neyman-Rubin framework

## Author Background

Scott Cunningham took an unconventional path — English major turned poet, then qualitative market researcher, before discovering economics through Gary Becker's Nobel speech. Studied econometrics at University of Georgia, developed the "Causal Inference and Research Design" course at Baylor in 2010, which became this book.

## Training

The author also offers **Mixtape Sessions** — workshops for learning the material directly. See the Mixtape Sessions tab on the website.

## See Also

- [causal_inference/methods](causal_inference/methods) — Detailed notes on each method
- [causal_inference/key_concepts](causal_inference/key_concepts) — Core theoretical concepts
