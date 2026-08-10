# Alpha Model Insight: `d5ZXQ3Ej` - Penta-Core Orthogonal Value & Revision Engine

## 1. Executive Summary
- **Alpha ID**: `d5ZXQ3Ej`
- **Quality Tier**: **SPECTACULAR / EXCELLENT CANDIDATE (SUBMITTABLE)**
- **Region / Universe**: US Equities (`USA`), `TOP3000`
- **Decay**: `10`
- **Truncation**: `0.08`
- **Neutralization**: `SUBINDUSTRY`
- **Delay**: `1`
- **Pasteurization**: `ON`

---

## 2. Quantitative Performance & IS Verification

| Metric | Measured Value | Passing Limit / Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | **1.50** | $\ge 1.25$ | **PASS** |
| **Fitness** | **1.13** | $\ge 1.00$ | **PASS** |
| **Annualized Returns** | **7.13%** | $> 0\%$ | **PASS** |
| **Turnover** | **5.97%** | $1.0\% \le \text{TO} \le 70.0\%$ | **PASS (Ideal Sweet Spot 5-8%)** |
| **Margin** | **23.90 bps** | $\ge 10.0\text{ bps}$ | **PASS (Top Tier > 20 bps)** |
| **Max Drawdown** | **8.50%** | $< 20.0\%$ | **PASS** |
| **Sub-Universe Sharpe** | **1.10** | $> 0.65$ | **PASS** |
| **Weight Concentration** | *No violations* | $< 10.0\%$ max weight | **PASS** |
| **Max Portfolio Correlation** | **0.6072** | $< 0.70$ | **PASS (Orthogonal)** |

---

## 3. Mathematical Formula & Structure

```fastexpr
ts_decay_linear(
    group_rank(est_ebit / cap, subindustry) 
    + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) 
    + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) 
    + group_rank(working_capital / assets, subindustry) 
    + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 
    10
)
```

---

## 4. Factor Decomposition & Economic Rationale

1. **Operating Profitability Yield (`est_ebit / cap`)**:
   - Captures expected corporate earnings yield scaled by market capitalization, neutral to industry accounting differences via `group_rank(..., subindustry)`.
2. **True Cash Generation (`free_cash_flow_reported_value / cap`)**:
   - Anchors the valuation to realized, cash-backed owner earnings, filtering out paper accounting anomalies.
3. **Analyst Consensus Revisions (`ts_delta(est_ebit, 30) / (abs(est_ebit) + 1)`)**:
   - Captures 30-day upward earnings estimate revisions by Wall Street sell-side analysts, driving fundamental post-earnings drift.
4. **Balance Sheet Liquidity & Working Capital (`working_capital / assets`)**:
   - Measures operational runway, short-term solvency, and capital buffer without debt dilution.
5. **Short-Term Mean Reversion Liquidity Filter (`-ts_delta(close, 4) / close`)**:
   - Monetizes short-term 4-day microstructure overreactions and liquidity demand shocks, providing favorable execution timing.
6. **Decay Smoothing (`ts_decay_linear(..., 10)`)**:
   - Reduces daily turnover to a low 5.97%, generating massive 23.90 bps margin per trade.

---

## 5. Pairwise Correlation Matrix vs Submitted Portfolio

Evaluated on daily return series across 1,235 common trading days:

| Submitted Alpha ID | Model Family / Strategy Core | Daily Return Pearson Corr | Daily Return Spearman Corr | Compliance Status |
| :--- | :--- | :--- | :--- | :--- |
| `88pomANl` | Triad PCR 270d + Asset Turn + Intraday | **0.6072** | 0.5830 | **PASS (< 0.70)** |
| `6Xpn9V2L` | Asset Turnover + Vol Arb Backfilled | **0.5315** | 0.5019 | **PASS (< 0.70)** |
| `Jjv1g3xO` | Implied Volatility Spread | **0.2493** | 0.2092 | **PASS (< 0.70)** |
| `d5RaEvVj` | Intraday Mean Reversion | **-0.0113** | 0.0564 | **PASS (< 0.70)** |
| `bldOZEjr` | Sales to EV Yield | **0.4793** | 0.4691 | **PASS (< 0.70)** |
| `RR1bxvea` | Asset Turnover Reversion | **0.3750** | 0.3871 | **PASS (< 0.70)** |
| `e7x3P7gO` | Target Price Premium | **0.2443** | 0.2562 | **PASS (< 0.70)** |
| `le3WZmdl` | Analyst Overpriced Sentiment | **0.4807** | 0.4056 | **PASS (< 0.70)** |
| `ZYKo6R78` | Cash Flow Momentum | **-0.0393** | -0.0422 | **PASS (< 0.70)** |

**Maximum Portfolio Correlation**: **`0.6072`** (Well below the platform threshold of `0.7000`).
