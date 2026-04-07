# Causal Inference — Key Theoretical Concepts

*Source: Causal Inference: The Mixtape (Cunningham)*

## 1. The Fundamental Problem of Causal Inference

A causal effect is the difference between two states of the world — what actually happened under treatment and what *would have happened* without it (the counterfactual). We can never observe both simultaneously for the same unit.

## 2. Potential Outcomes Framework (Rubin Causal Model)

- Each unit has two potential outcomes: **Y¹** (treated) and **Y⁰** (untreated)
- **Individual treatment effect:** τᵢ = Y¹ᵢ - Y⁰ᵢ (unobservable)
- **Average Treatment Effect (ATE):** E[Y¹ - Y⁰]
- **Average Treatment Effect on the Treated (ATT):** E[Y¹ - Y⁰ | D=1]
- **SUTVA** (Stable Unit Treatment Value Assumption): One unit's treatment doesn't affect another's outcomes

## 3. Selection Bias

The simple difference in outcomes between treated and untreated groups conflates the causal effect with **selection bias** — systematic differences between groups unrelated to treatment. All causal inference methods aim to eliminate or reduce this bias.

**Simple Difference Decomposition:**
E[Y|D=1] - E[Y|D=0] = ATE + Selection Bias

## 4. Directed Acyclical Graphs (DAGs)

Developed by Judea Pearl; graphical representation of causal relationships:

- **Nodes** = random variables
- **Arrows** = causal effects (direction of arrow = direction of causality)
- **Missing arrows** = strong claim of no causal relationship
- **Direct path:** D → Y (causal)
- **Backdoor path:** D ← X → Y (spurious correlation via confounder)

### Key DAG Concepts:
- **Confounder:** Variable that causes both treatment and outcome (opens backdoor path)
- **Collider:** Variable caused by two other variables (D → X ← Y); conditioning on a collider *opens* a spurious path (collider bias)
- **Backdoor Criterion:** Block all backdoor paths from D to Y to identify causal effect
- **Mediator:** Variable on the causal pathway D → X → Y

## 5. Conditional Independence Assumption (CIA)

Also called "selection on observables." Treatment assignment is as good as random *conditional* on observable covariates X:

(Y¹, Y⁰) ⊥ D | X

If CIA holds, you've found a conditioning strategy that satisfies the backdoor criterion.

## 6. Identification vs. Estimation

- **Identification:** Can you *in principle* recover the causal effect given infinite data?
- **Estimation:** Given that it's identified, how do you compute it from finite data?

Identification comes from assumptions and research design; estimation comes from statistical methods.

## 7. Internal vs. External Validity

- **Internal validity:** Is the causal estimate correct for the study population?
- **External validity:** Does it generalize to other populations/settings?

## 8. Key Historical Figures

| Person | Contribution |
|--------|-------------|
| R.A. Fisher | Randomization as basis for causal inference (1935) |
| Jerzy Neyman | Potential outcomes framework (1923) |
| Donald Rubin | Formalized potential outcomes model (1974) |
| Judea Pearl | DAGs, do-calculus, backdoor criterion |
| Philip Wright | Invented instrumental variables (1928) |
| Donald Campbell | Invented regression discontinuity (1960) |
| John Snow | Early difference-in-differences (cholera, 1855) |

## See Also

- [causal_inference/overview](causal_inference/overview)
- [causal_inference/methods](causal_inference/methods)
