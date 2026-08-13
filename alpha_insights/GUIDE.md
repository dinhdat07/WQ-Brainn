# Alpha Insights - Tracking and Development Guide

This guide establishes the convention for tracking ideas, experiments, and successful models throughout the Alpha development lifecycle on WorldQuant Brain. 

## 1. Directory Structure

Each phase must be tracked in its own dedicated folder to prevent clutter and maintain historical context.

```text
alpha_insights/
  ├── phases/
  │   ├── phase_01/
  │   ├── phase_02/
  │   └── phase_15/
  │       ├── ideas/            # Raw ideas, formulations, hypotheses
  │       ├── experiments/      # Simulation results, Sharpe ratios, failures
  │       └── models/           # ONLY API-Accepted alphas with Uniqueness passing
  └── GUIDE.md                  # This file
```

## 2. Tracking Conventions

### 2.1 Ideas (`/ideas/`)
- **Format:** `[ID]_IdeaName.md`
- **Content:** Must include the core rationale, the mathematical formula, decay, universe, and expected interaction.
- **Rule:** Do not mix test results here. This is purely for hypotheses.

### 2.2 Experiments (`/experiments/`)
- **Format:** `[Date]_[Theme]_results.md` (e.g., `2026-08-01_Fundamental_results.md`)
- **Content:** Logs of simulation outputs (Sharpe, Fitness, Turnover) and the Alpha IDs.
- **Rule:** Clearly highlight **FAILURES** and **WHY** they failed (e.g., "Failed due to Self-Correlation > 0.7").

### 2.3 Successful Models (`/models/`)
- **Format:** `[AlphaID]_SUCCESS.md` (e.g., `9qppnrPV_SUCCESS.md`)
- **Content:** 
  - Formula, Settings (Decay, Truncation, Region).
  - Out-of-Sample metrics (IS vs OS Sharpe, Uniqueness).
  - Acknowledgment of API `201 Accepted` status.
- **Rule:** **ONLY** models that successfully passed the API `/submit` endpoint (including passing the `SELF_CORRELATION` check) are allowed here. If a model has a Sharpe > 2.0 but gets rejected for correlation, it stays in `/experiments/` as a `[AlphaID]_REJECTED.md`.

## 3. Workflow for Agent Interactions

1. **Ideation**: Generate theoretical formulas based on constraints (e.g., Target Turnover < 10%, Sharpe > 1.5). Log to `ideas/`.
2. **Simulation**: Run Python evaluators. Log raw metrics to `experiments/`.
3. **Submission**: If Sharpe > 1.25, call `/submit`. 
4. **Verification**: Check API response.
   - If `201 Accepted` AND passes correlation checks -> move to `models/[ID]_SUCCESS.md`.
   - If Rejected (Self-Corr > 0.7, etc.) -> move to `experiments/[ID]_REJECTED.md`.
5. **Phase Conclusion**: A phase is **ONLY** considered complete when at least ONE alpha is successfully accepted into the `models/` folder. Do not close a phase on failures.
