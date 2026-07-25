---
name: wq-alpha-workflow
description: Standard workflow and 5-step process for building, tuning, and optimizing WorldQuant Brain Alpha models to pass IS tests (Sharpe, Fitness, Turnover, Self-Correlation). Use when developing or tuning WQ Brain alphas.
risk: unknown
source: local
---

# WQ Alpha Workflow & Decision Matrix

Use this as the canonical workflow for building and optimizing Alpha models for WorldQuant Brain. 
The primary goal is to achieve passing In-Sample (IS) metrics: Sharpe > 1.25, Fitness > 1.0, Turnover between 1% and 70%, and Self-Correlation < 0.7.

## Terminology
- **Batch**: A set of formulas tested in one simulation run (e.g., `Batch <Order> - <Size>`).
- **Phase**: A complete research cycle containing multiple batches. A Phase ends when a SUBMITTABLE model is found and successfully submitted.

## Step 1: Research & Ideation (Tự học và tìm ý tưởng)
Before writing any code, you MUST research new alpha concepts to ensure diversity:
1. **Local Knowledge**: Read `alpha_insights/core_knowledge/dictionary.md` to see what has already been submitted and what failed.
2. **Local Research**: Read files in `research-doc/` (e.g., `deep-research-report.md`) for verified formulaic structures.
3. **Internet Research**: Use `search_web` to look up new quantitative alpha concepts (e.g., "WorldQuant Alpha 101", "SSRN quantitative momentum", "Quantpedia trading strategies"). Combine these web insights with the available API data fields.

## Step 2: Source Ideas & Data Selection (Chống Self-Correlation)
- **CRITICAL RULE**: Do NOT reuse or slightly mutate the core datasets of previously submitted alphas (found in `alpha_insights/core_knowledge/dictionary.md`). If the current pool uses Price Momentum (`close`, `returns`), you MUST use Alternative Data (Analyst Estimates, Fundamentals, Options, Sentiment) to avoid hitting `Self-Correlation > 0.9`.
- **Cross-pollination**: Combine unrelated datasets (e.g., Fundamentals + Options Volatility) to create highly unique, uncorrelated signals.

## Step 3: Core Logic Testing (Thử nghiệm Lõi)
- Develop a basic mathematical hypothesis (e.g., "Overpriced stocks have high target prices and cash flows").
- Test the core formula (e.g., `-ts_corr(est_ptp, est_fcf, 252)`) with a long lookback period (e.g., 252 days) to establish a baseline Sharpe and Fitness.
- The goal is to find a signal that yields a positive Sharpe and low Self-Correlation.

## Step 4: Server Evaluation Decision Matrix (Xử lý lỗi)
When the server returns the simulation evaluation, use this strict Decision Matrix to handle the situation:

| Server Result / Error | Diagnosis | Required Action |
| :--- | :--- | :--- |
| **API Error / Invalid Field** | The requested field does not exist or is unsupported. | Use `search_fields.py` to find the correct field name, or use `ts_backfill` if it's a NaN issue. |
| **CONCENTRATED_WEIGHT** | Capital is too concentrated (>10%) in a few sparse assets. | 1. Change grouping from `group_rank(..., sector)` to flat `rank(...)` across a broader universe (e.g., `TOP3000`).<br>2. Use `ts_backfill(DATA, 60)` to forward-fill sparse data (e.g., options).<br>3. Optionally, tighten truncation (e.g., `truncation: 0.05`). |
| **LOW_FITNESS (Fitness < 1.0)** | Signal is too noisy, Turnover is too high, excessive trading costs. | Wrap the core signal in a smoothing function: `ts_decay_linear(SIGNAL, 5)`. |
| **LOW_SHARPE (Sharpe < 1.25)** | Signal reacts too slowly to market changes (too much lag). | Drastically reduce the lookback window (e.g., from 252 days down to 20-60 days) to increase responsiveness. |
| **HIGH_CORRELATION (> 0.7)** | The core concept is too similar to an existing submitted alpha. | **ABANDON** the current dataset. Go back to Step 1 and find a completely new data source from `research-doc` or the internet. |
| **SUCCESS (Sharpe>1.25, Fit>1.0)** | The model passes all IS requirements. | Run the submission script to submit it to OS testing! |

## Step 5: Output Format, Logging & Phase Cleanup
This workflow follows a strict two-level structure: **Batches** and **Phases**.

### Post-Batch Actions (During a Phase)
After running a simulation batch:
1. Log the batch metrics (Sharpe/Fitness/Turnover) and insights in `alpha_insights/experiment_logs/mutation_experiments_log.md` (or `failed_experiments_log.md` if the approach completely failed).
2. Use the strict format: `Batch <Order> - <Size>` (e.g., `Batch 1 - 10`).
3. Iterate based on the Decision Matrix (Step 4).

### Post-Phase Actions (Phase Completion)
A Phase officially ends when you find an Alpha that passes the IS test (Sharpe>1.25, Fit>1.0, Corr<0.7) and is successfully submitted. You MUST execute these steps:
1. **Clean Repo:** Delete any temporary scratch scripts, unneeded logs, or leftover files from the batch testing process.
2. **Document Success:** Create a detailed profile of the successful alpha in `alpha_insights/successful_models/` (e.g., `[Alpha_ID]_[Concept].md`).
3. **Update Core Knowledge:** Add the successful Alpha to the Hall of Fame in `alpha_insights/core_knowledge/dictionary.md` and document any new overarching lessons in `model_development_process.md`.
4. **Git Commit:** Commit all changes with a descriptive message: `feat(alpha): Phase X completed - [Model Name]`.

## When to Use
- When asked to build a new alpha for WorldQuant Brain.
- When an existing alpha fails due to `LOW_FITNESS`, `CONCENTRATED_WEIGHT`, or `HIGH_CORRELATION`.
- When you need to research new quantitative strategies from the web or local documents.

## Limitations
- This workflow is specific to WorldQuant Brain API constraints.
- `ts_backfill` is powerful but can introduce look-ahead bias if misused on non-point-in-time data (WQ Brain datasets are already point-in-time safe, so this is generally acceptable).
