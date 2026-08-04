---
name: wq-alpha-workflow
description: Gold-tier workflow for building, tuning, and submitting WorldQuant Brain Alpha models. Optimized for the 3-dimension scoring system (IS Score, Uniqueness, Days of Submission). Includes uniqueness-first research methodology, self-correlation avoidance, and daily submission cadence strategy.
risk: unknown
source: local
---

# WQ Alpha Workflow & Decision Matrix (Gold Tier)

Use this as the canonical workflow for building and optimizing Alpha models for WorldQuant Brain.

## Competition Context: Gold Tier Scoring

> **CRITICAL**: Gold tier uses a **3-dimension scoring system**. Your Total Score is an equal-weighted combination of how you rank on each dimension:

| Dimension | Weight | What It Measures | How to Climb |
|:---|:---:|:---|:---|
| **IS Score** | 1/3 | In-sample quality (Sharpe, Fitness, Turnover, Drawdown) | Build high-Sharpe, high-Fitness models |
| **Uniqueness** | 1/3 | How differentiated your alphas are from ALL other competitors | Use novel data sources, unique logic, avoid common patterns |
| **Days of Submission** | 1/3 | Consistency of submitting new alphas daily | Submit at least 1 new alpha EVERY day |

### Strategic Implications
1. **Days of Submission is the most controllable** — never miss a day of submitting.
2. **Uniqueness rewards differentiated research** — the more unique your signal, the higher you rank on this axis. Avoid popular patterns (e.g., simple momentum, simple value).
3. **IS Score** remains important but is no longer the ONLY dimension. A "Good" alpha with high uniqueness can outrank a "Spectacular" alpha that's common.

## Terminology
- **Batch**: A set of formulas tested in one simulation run (e.g., `Batch <Order> - <Size>`).
- **Phase**: A complete research cycle containing multiple batches. A Phase ends when a SUBMITTABLE model is found and successfully submitted.
- **Signal Cluster**: A group of alphas using the same core economic logic (e.g., "Options Skew", "Asset Turnover", "Intraday Reversion"). Alphas within the same cluster are highly correlated.

---

## Step 1: Research & Ideation (Uniqueness-First)

Before writing any code, you MUST research new alpha concepts with **uniqueness as the primary objective**:

### 1.1 Review Existing Portfolio (Anti-Correlation Check)
1. **Read `alpha_insights/core_knowledge/dictionary.md`** to see ALL submitted models and their signal clusters.
2. **Identify saturated clusters** — clusters with 2+ submitted alphas are SATURATED. Do NOT submit more variants.
3. **Identify untouched data categories** — check which of the 8 data categories (fundamental, analyst, news, pv, option, model, socialmedia, univ1) have NOT been used yet.

### 1.2 Explore Untapped Data Fields
1. **Local Field Database**: Use the complete field catalog at `wq-alpha-research/references/wq_usa_top3000_delay1_data_fields.json` (4367 fields across 8 categories).
2. **Low-alphaCount Mining**: Search for fields with `alphaCount < 50` — these are underexplored by other competitors and maximize Uniqueness.
3. **Cross-Category Hybridization**: Combine fields from different categories (e.g., `news` × `fundamental`, `socialmedia` × `option`) to create truly novel signals.

### 1.3 External Research
1. **Academic Literature**: Search SSRN, Quantpedia, Journal of Financial Economics for novel factor ideas NOT commonly implemented.
2. **101 Alphas Paper**: Reference `research-doc/101-alpha.pdf` for formulaic patterns, but **transform them significantly** — direct copies will score low on Uniqueness.
3. **Internet Research**: Use `search_web` for cutting-edge quant strategies (e.g., "alternative data alpha signals", "machine learning factor investing", "microstructure signals").

### 1.4 Uniqueness Amplification Techniques
To maximize the Uniqueness dimension:
- **Use rare operators**: `ts_regression`, `ts_corr`, `ts_covariance`, `trade_when` with complex conditions.
- **Use rare data fields**: Fields from `news`, `socialmedia`, `model` categories are far less common than `pv` or `fundamental`.
- **Use non-standard time horizons**: Instead of common lookbacks (5, 10, 21, 63, 126, 252), try unusual windows (7, 14, 45, 90, 180).
- **Use custom groupings**: `group_rank(..., sector)` or `group_rank(..., market)` instead of the ubiquitous `subindustry`.

---

## Step 2: Orthogonality Design (Chống Self-Correlation)

### 2.1 Signal Cluster Map (What's Already Submitted)
Maintain awareness of your submitted portfolio's signal clusters. Signals within the same cluster WILL have Self-Correlation > 0.7.

**Known Saturated Clusters** (as of Phase 10):
| Cluster | Core Signal | Submitted Count | Status |
|:---|:---|:---:|:---|
| Options Skew | `implied_volatility_call - put` | 3+ | ⛔ SATURATED |
| Asset Turnover | `sales / assets` | 4+ | ⛔ SATURATED |
| Intraday Reversion | `-(close - open) / open` | 2+ | ⛔ SATURATED |
| Institutional Triad | Above 3 combined | 2+ | ⛔ SATURATED |
| Analyst Estimates | `est_eps`, `est_ptp` | 2+ | ⚠️ NEAR SATURATED |

### 2.2 The Principal Component Trap (CRITICAL LESSON)
> **PROVEN FACT**: In the USA TOP3000 universe, `Fundamental Value` + `Options Skew` + `Reversion` captures the peak of predictive variance. ANY variation of this combination (F-Scores, Mixed Decays, parameter tuning) collapses to Self-Correlation > 0.90 with existing submitted alphas.
>
> **The ONLY way to achieve orthogonal alphas is to use COMPLETELY DIFFERENT data sources and economic logic.**

### 2.3 Orthogonal Signal Families (Untouched Territories)
These signal families are expected to have LOW correlation with the existing portfolio:

| Family | Data Category | Example Fields | Expected Uniqueness |
|:---|:---|:---|:---:|
| **News Sentiment** | news | `news_sentiment`, `news_pct_1min`, `news_max_up_ret` | ⭐⭐⭐⭐⭐ |
| **Social Media Buzz** | socialmedia | `scl12_buzz`, `scl12_bullscore` | ⭐⭐⭐⭐⭐ |
| **Peer Relative Returns** | pv | `rel_ret_all`, `cum_rel_return` | ⭐⭐⭐⭐ |
| **Accruals & Quality** | fundamental | `accruals`, `working_capital_changes` | ⭐⭐⭐⭐ |
| **Regression Trends** | fundamental | `ts_regression(..., rettype=2)` on rare fields | ⭐⭐⭐⭐ |
| **Inventory/Supply Chain** | fundamental | `inventories`, `cost_of_goods_sold` | ⭐⭐⭐⭐ |
| **Bull/Bear Traps** | news+pv | `news_pct_1min` × `slope` patterns | ⭐⭐⭐⭐⭐ |
| **Volatility Regime** | option+pv | `parkinson_volatility` vs `implied_volatility` ratio changes | ⭐⭐⭐ |
| **Model Factors** | model | `fscore_*` proprietary factors | ⭐⭐⭐ |
| **Earnings Momentum** | analyst | `est_cashflow_op` trends, `est_capex` changes | ⭐⭐⭐ |

### 2.4 Pre-Submission Correlation Check (MANDATORY)
Before submitting ANY new alpha, you MUST:
1. Run `check_exact_submitted_corr.py <ALPHA_ID>` against ALL submitted alphas.
2. Verify **Daily Return Correlation < 0.70** against every submitted alpha.
3. If correlation ≥ 0.70, the alpha WILL be rejected unless its Sharpe is ≥ 10% higher than the conflicting alpha.

---

## Step 3: Formula Design & Testing

### 3.1 Uniqueness-First Template Library

**Tier 1: High Uniqueness (News & Sentiment)**
```fastexpr
-- Bull Trap Detector (from Silver Example #6)
slope = ts_regression(ts_backfill(news_pct_1min, 60), ts_step(1), 5, rettype = 2);
winsorize(-ts_backfill(news_max_up_ret, 60) * abs(slope), std = 4)

-- News Buzz Acceleration
ts_decay_linear(rank(ts_av_diff(ts_backfill(scl12_buzz, 20), 60)), 10)

-- Sentiment-Adjusted Fundamentals
group_rank(ts_backfill(news_sentiment, 30) * rank(operating_income / equity), subindustry)
```

**Tier 2: High Uniqueness (Peer & Relative)**
```fastexpr
-- 5-Day Peer Performance Gap (from Silver Example #3)
cum_rel = (1 + ts_delay(rel_ret_all, 4)) * (1 + ts_delay(rel_ret_all, 3)) * (1 + ts_delay(rel_ret_all, 2)) * (1 + ts_delay(rel_ret_all, 1)) * (1 + rel_ret_all);
cum_ret = (1 + ts_delay(returns, 4)) * (1 + ts_delay(returns, 3)) * (1 + ts_delay(returns, 2)) * (1 + ts_delay(returns, 1)) * (1 + returns);
cum_rel - cum_ret

-- Relative Return Momentum
ts_decay_linear(group_rank(ts_sum(rel_ret_all, 21), sector), 10)
```

**Tier 3: Moderate Uniqueness (Quality & Accruals)**
```fastexpr
-- FCF Quality (from Silver Example #5)
ts_decay_linear(ts_scale(est_cashflow_op, 252), 22) - ts_decay_linear(ts_scale(est_capex, 252), 22)

-- Long-Term Investment Trend (from Silver Example #4)
ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2)

-- Inventory Efficiency
group_rank(ts_rank(cost_of_goods_sold / inventories, 126), subindustry)
```

### 3.2 Settings Decision Matrix

| Signal Type | Decay | Neutralization | Truncation | nanHandling | Expected TO |
|:---|:---:|:---:|:---:|:---:|:---:|
| News/Sentiment | 4-10 | INDUSTRY | 0.05-0.08 | ON | 8-30% |
| Peer Relative | 0-10 | SECTOR | 0.08 | OFF | 15-40% |
| Fundamental Quality | 0 | SUBINDUSTRY | 0.08 | ON | 2-8% |
| Accruals/Inventory | 0-4 | SUBINDUSTRY | 0.08 | ON | 5-15% |
| Mixed/Hybrid | 4-20 | INDUSTRY/SUBINDUSTRY | 0.08 | ON | 10-20% |
| Regression Trend | 0 | SUBINDUSTRY | 0.08 | ON | 1-5% |
| Market-Neutral (corr break) | 0-25 | MARKET | 0.08 | ON | 5-15% |

---

## Step 4: Server Evaluation Decision Matrix

| Server Result / Error | Diagnosis | Required Action |
|:---|:---|:---|
| **API Error / Invalid Field** | Field doesn't exist or unsupported. | Use field search script or `rank(field)` to validate. |
| **CONCENTRATED_WEIGHT** | Capital too concentrated in sparse assets. | 1. Use `rank(...)` instead of `group_rank(..., sector)`. 2. Use `ts_backfill(DATA, 60)`. 3. Tighten truncation to 0.05. |
| **LOW_FITNESS (< 1.0)** | Signal too noisy, Turnover too high. | Wrap in `ts_decay_linear(SIGNAL, 5-15)`. |
| **LOW_SHARPE (< 1.25)** | Signal too weak. | Reduce lookback window (252 → 60 days), try `group_rank` + `ts_rank` combo. |
| **LOW_SUB_UNIVERSE_SHARPE** | Alpha only works in large-caps. | Add a universally-available signal pillar (e.g., `-(close-open)/open` works across all cap sizes). |
| **SELF_CORRELATION (≥ 0.7)** | Core concept too similar to existing submitted alpha. | **ABANDON** this signal cluster entirely. Switch to a different data category (Step 2.3). |
| **SUCCESS (All checks PASS)** | Ready for submission. | Run correlation check, then submit. |

---

## Step 5: Daily Submission Strategy

### 5.1 The Daily Cadence
Since **Days of Submission** is 1/3 of the total score:
1. **Aim to submit at least 1 new alpha EVERY day.**
2. Maintain a **pipeline of 3-5 ready-to-submit candidates** at all times.
3. If stuck on "Spectacular" models, submit "Good" tier models (Sharpe 1.25-1.75) from untouched signal families — they score higher on Uniqueness than a perfect model from a crowded family.

### 5.2 Signal Diversity Pipeline
Organize your research into a rotating pipeline across signal families:

```
Week 1: News & Sentiment signals (news_pct_1min, news_sentiment, scl12_buzz)
Week 2: Peer & Relative returns (rel_ret_all, cum_rel_return)
Week 3: Quality & Accruals (accruals, working_capital, inventory efficiency)
Week 4: Regression Trends & Long-Term Investment (ts_regression patterns)
Repeat with new variations...
```

### 5.3 "Good Enough" Submission Thresholds
For daily submission cadence, accept models that meet these minimum thresholds:
- **Sharpe ≥ 1.25** (minimum IS requirement)
- **Fitness ≥ 1.0**
- **Turnover 1% - 70%**
- **Self-Correlation < 0.70** against ALL submitted alphas
- **All IS checks PASS**

A "Good" alpha with high Uniqueness is MORE VALUABLE than a "Spectacular" alpha with low Uniqueness.

---

## Step 6: Output Format, Logging & Phase Cleanup

### Post-Batch Actions
After running a simulation batch:
1. Log batch metrics in `alpha_insights/experiment_logs/mutation_experiments_log.md`.
2. Use format: `Batch <Order> - <Size>` (e.g., `Batch 1 - 10`).
3. Track **Uniqueness indicators**: which data fields used, which operators, what economic logic.

### Post-Phase Actions (Phase Completion)
A Phase ends when a SUBMITTABLE alpha is found and successfully submitted:
1. **Document Success**: Create detailed profile in `alpha_insights/successful_models/[Alpha_ID]_[Concept].md`.
2. **Update Core Knowledge**: Add to `alpha_insights/core_knowledge/dictionary.md` Hall of Fame.
3. **Update Signal Cluster Map**: Mark which clusters are now SATURATED.
4. **Log failures** in `alpha_insights/experiment_logs/failed_experiments_log.md` with root cause analysis.

---

## Step 7: Advanced Research Directions (Untapped Alpha Sources)

### 7.1 News Microstructure Signals
The `news` category has **996 fields** but very few submitted alphas. Key fields:
- `news_pct_1min`: First-minute price reaction to news — captures informed trading.
- `news_max_up_ret` / `news_max_down_ret`: Maximum post-news return — identifies overreaction.
- `news_sentiment`: Aggregated sentiment score — directly predicts short-term returns.
- `news_count_*`: News volume — "buzz" as a contrarian or momentum indicator.

**Strategy**: Use `ts_regression` on `news_pct_1min` to extract the *slope* of reactions over 5-10 days. A deteriorating slope combined with a recent spike signals a "bull trap."

### 7.2 Social Media Signals
The `socialmedia` category has **22 fields** — extremely underexplored:
- `scl12_buzz`: Social media mentions volume.
- `scl12_bullscore` / `scl12_bearscore`: Bullish/bearish sentiment ratios.
- `scl12_total_scanned_count`: Total social posts analyzed.

**Strategy**: Buzz acceleration (rate of change of buzz) often precedes price moves. Combine with fundamental quality to avoid meme-stock traps.

### 7.3 Regression-Based Trend Extraction
`ts_regression` is a powerful but underutilized operator:
- `ts_regression(signal, ts_step(1), N, rettype=2)`: Extracts the *slope* (trend) of a signal over N days.
- Apply to fundamental fields (investment trends, revenue growth) for ultra-low-turnover signals.
- Apply to news/sentiment fields for medium-frequency signals.

### 7.4 Peer Relative Returns
`rel_ret_all` measures how a stock performs relative to its peers:
- **Mean-reversion**: Stocks lagging their peers tend to catch up.
- **Momentum**: Stocks leading their peers may continue to lead.
- **Condition**: Use `trade_when` to only trade when the gap is significant.

### 7.5 Custom Neutralization Patterns
Instead of standard neutralizations, create custom groupings:
```fastexpr
-- Custom volatility buckets
group_rank(signal, bucket(20, rank(ts_std_dev(returns, 60))))

-- Floor-based size groups
group_rank(signal, floor(rank(cap) * 5))
```

---

## Appendix A: Submitted Alpha Portfolio Summary

| Alpha ID | Signal Cluster | Core Logic | Phase |
|:---|:---|:---|:---:|
| 88pomANl | Institutional Triad | Asset Turn + Options Skew + Intraday Rev | 9 |
| 6Xpn9V2L | Asset Turn + VolArb | Backfilled volatility arbitrage | 8 |
| Jjv1g3xO | Options Skew | IV Spread 270d | 7 |
| d5RaEvVj | Intraday Reversion | Group zscore reversion | 6 |
| bldOZEjr | Fundamental Value | Sales to EV yield | - |
| RR1bxvea | Asset Turnover Reversion | Combined | - |
| e7x3P7gO | Analyst Target | Target price premium | - |
| le3WZmdl | Analyst Overpriced | Overpriced signal | - |
| ZYKo6R78 | Cash Flow Momentum | FCF momentum | - |
| 2rpzj59P | Market Neutral Triad | Triad w/ MARKET neutralization | 10 |

### Saturated Data Sources (DO NOT reuse as primary signal):
- `sales / assets` (4+ alphas)
- `implied_volatility_call/put_*` (3+ alphas)
- `-(close - open) / open` (2+ alphas)
- `est_eps / close`, `est_ptp` (2+ alphas)

### Fresh Data Sources (HIGH priority for new research):
- `news_*` fields (996 available, ~0 submitted)
- `scl12_*` social media fields (22 available, ~0 submitted)
- `rel_ret_all` peer returns (~0 submitted)
- `inventories`, `cost_of_goods_sold` (~0 submitted)
- `ts_regression` trend patterns (~1 submitted)

---

## Appendix B: Quick Reference — Operators

| Type | Operators | Use |
|:---|:---|:---|
| Cross-sectional | `rank(x)`, `zscore(x)`, `normalize(x)`, `scale(x)`, `winsorize(x, std=4)` | Standardize across all stocks daily |
| Time-series | `ts_mean`, `ts_std_dev`, `ts_delta`, `ts_rank`, `ts_corr`, `ts_decay_linear`, `ts_backfill`, `ts_zscore`, `ts_regression`, `ts_sum`, `ts_covariance` | Single-stock historical window |
| Grouping | `group_rank(x, group)`, `group_neutralize(x, group)`, `group_zscore(x, group)`, `group_backfill(x, group, N)` | Within-group neutralization |
| Conditional | `if_else(cond, a, b)`, `trade_when(x, cond, delay)` | Conditional exposure |
| Vector | `vec_avg(a, b, c)`, `vec_sum(a, b, c)` | Multi-field element-wise ops |
| Math | `abs(x)`, `floor(x)`, `bucket(N, x)`, `log(x)`, `sign(x)`, `max(a, b)`, `min(a, b)` | Mathematical transforms |

**Golden Combo**: `group_rank(ts_rank(signal, N), subindustry)` — high pass rate for fundamental signals.

---

## Appendix C: Core Lessons (One-Liner Version)

1. **Uniqueness > Sharpe in Gold tier** — a Good alpha with novel signal beats a Spectacular alpha with common signal.
2. **Submit every single day** — Days of Submission is the easiest dimension to max out.
3. **201 response ≠ submission success** — always verify `status == ACTIVE` after submitting.
4. **Daily returns correlation, NOT cumulative PnL** — cumulative PnL correlations are misleadingly high (>0.90).
5. **The Principal Component Trap** — `Fundamental + Options + Reversion` captures peak variance; variations are mathematically unable to be orthogonal.
6. **Explore the 996 news fields and 22 social media fields** — these are the most underexplored data sources.
7. **`ts_regression(..., rettype=2)`** extracts trends from any signal — extremely powerful for long-horizon alphas.
8. **Switching neutralization to MARKET** breaks correlation but drops Sharpe — use as a "correlation breaker" when needed.
9. **Keep 3-5 candidates ready** in a pipeline so you never miss a submission day.
10. **group_rank + ts_rank is the golden combo** for fundamental signals, but for uniqueness, combine with rare operators like `ts_regression`, `trade_when`, or `winsorize`.
