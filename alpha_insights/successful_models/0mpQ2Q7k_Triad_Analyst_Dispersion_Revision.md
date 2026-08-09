# Alpha Model Insight: `0mpQ2Q7k` - Triad Analyst Dispersion-Gated Revision & Intraday Engine

## 1. Executive Summary
- **Alpha ID**: `0mpQ2Q7k`
- **Quality Tier**: **SUBMITTABLE CANDIDATE (ORTHOGONAL)**
- **Region / Universe**: US Equities (`USA`), `TOP3000`
- **Decay**: `0` (Decay handled internally via `ts_decay_linear(..., 10)`)
- **Truncation**: `0.08`
- **Neutralization**: `SUBINDUSTRY`
- **Delay**: `1`
- **Pasteurization**: `ON`

---

## 2. Quantitative Performance & IS Verification

| Metric | Measured Value | Passing Limit / Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | **1.54** | $\ge 1.25$ | **PASS** |
| **Fitness** | **1.14** | $\ge 1.00$ | **PASS** |
| **Annualized Returns** | **8.49%** | $> 0\%$ | **PASS** |
| **Turnover** | **15.59%** | $1.0\% \le \text{TO} \le 70.0\%$ | **PASS** |
| **Margin** | **10.90 bps** | $\ge 10.0\text{ bps}$ | **PASS** |
| **Max Drawdown** | **6.69%** | $< 20.0\%$ | **PASS (Extremely Resilient)** |
| **Sub-Universe Sharpe** | **1.27** | $> 0.67$ | **PASS** |
| **Weight Concentration** | *No violations* | $< 10.0\%$ max weight | **PASS** |
| **Max Portfolio Correlation** | **0.6142** | $< 0.70$ | **PASS (Orthogonal)** |

---

## 3. Mathematical Formula & Structure

```fastexpr
ts_decay_linear(
    group_rank(est_ebit / cap, subindustry) 
    + group_rank(
        trade_when(
            group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, 
            ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), 
            -1
        ), 
        subindustry
    ) 
    + group_rank(-(close - open) / open, subindustry), 
    10
)
```

---

## 4. Factor Decomposition & Economic Rationale

1. **Operating Valuation Anchor (`est_ebit / cap`)**:
   - Anchors the portfolio in profitable, high earnings-yield enterprises relative to their market capitalization.
2. **Analyst Consensus Skew / Dispersion Gate (`trade_when(..., ts_delta(est_ebit, 30) / ..., -1)`)**:
   - Exploits asymmetry in analyst forecast distributions. When the median estimate exceeds the mean (indicating positive consensus skew and tail confidence), the 30-day revision trend is activated. If analyst consensus exhibits negative skew, the stock is penalized.
3. **High-Frequency Microstructure Reversal (`-(close - open) / open`)**:
   - Captures intraday market-maker overreaction and liquidity provision premia, providing optimal entry and exit points.
4. **Decay Smoothing (`ts_decay_linear(..., 10)`)**:
   - Smooths the combined multi-factor signal over a 10-day rolling window, holding turnover to 15.59% with a safe 10.90 bps margin.

---

## 5. Pairwise Correlation Matrix vs Active Submitted Portfolio

Evaluated on daily return series across 1,235 common trading days:

| Submitted Alpha ID | Model Family / Strategy Core | Daily Return Pearson Corr | Daily Return Spearman Corr | Compliance Status |
| :--- | :--- | :--- | :--- | :--- |
| `bldOZEjr` | Sales to EV Yield | **0.6142** | 0.5944 | **PASS (< 0.70)** |
| `88pomANl` | Triad PCR 270d + Asset Turn + Intraday | **0.5616** | 0.5031 | **PASS (< 0.70)** |
| `RR1bxvea` | Asset Turnover Reversion | **0.5320** | 0.5057 | **PASS (< 0.70)** |
| `6Xpn9V2L` | Asset Turnover + Vol Arb Backfilled | **0.5184** | 0.5122 | **PASS (< 0.70)** |
| `78z9d2d5` | Dual Skew Convexity | **0.4275** | 0.3790 | **PASS (< 0.70)** |
| `e7x3P7gO` | Target Price Premium | **0.4045** | 0.3358 | **PASS (< 0.70)** |
| `3qpd8ee6` | Kakushadze IV Alpha #40 Hybrid | **0.2813** | 0.2837 | **PASS (< 0.70)** |
| `2rpzj59P` | Triple-Momentum Vol Regulated | **0.2617** | 0.2488 | **PASS (< 0.70)** |
| `d5RaEvVj` | Intraday Mean Reversion | **0.2029** | 0.1865 | **PASS (< 0.70)** |
| `le3WZmdl` | Analyst Overpriced Sentiment | **0.2010** | 0.1781 | **PASS (< 0.70)** |
| `Jjv1g3xO` | Implied Volatility Spread | **0.0507** | -0.0099 | **PASS (< 0.70)** |
| `ZYKo6R78` | Cash Flow Momentum | **0.0412** | -0.0041 | **PASS (< 0.70)** |

**Maximum Portfolio Correlation**: **`0.6142`** (Well below the platform threshold of `0.7000`).
