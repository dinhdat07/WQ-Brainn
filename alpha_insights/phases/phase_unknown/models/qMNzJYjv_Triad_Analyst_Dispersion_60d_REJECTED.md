# Alpha Model Insight: `qMNzJYjv` - Triad Analyst Dispersion 60d Consensus Engine

## 1. Executive Summary
- **Alpha ID**: `qMNzJYjv`
- **Quality Tier**: **SUBMITTABLE CANDIDATE (SUPER ORTHOGONAL)**
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
| **Sharpe Ratio** | **1.49** | $\ge 1.25$ | **PASS** |
| **Fitness** | **1.10** | $\ge 1.00$ | **PASS** |
| **Annualized Returns** | **8.10%** | $> 0\%$ | **PASS** |
| **Turnover** | **14.79%** | $1.0\% \le \text{TO} \le 70.0\%$ | **PASS** |
| **Margin** | **10.95 bps** | $\ge 10.0\text{ bps}$ | **PASS** |
| **Max Drawdown** | **7.23%** | $< 20.0\%$ | **PASS** |
| **Sub-Universe Sharpe** | **1.12** | $> 0.65$ | **PASS** |
| **Weight Concentration** | *No violations* | $< 10.0\%$ max weight | **PASS** |
| **Max Portfolio Correlation** | **0.5686** | $< 0.70$ | **PASS (Super Orthogonal)** |

---

## 3. Mathematical Formula & Structure

```fastexpr
ts_decay_linear(
    group_rank(est_ebit / cap, subindustry) 
    + group_rank(
        trade_when(
            group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, 
            ts_delta(est_ebit, 60) / (abs(est_ebit) + 1), 
            -1
        ), 
        subindustry
    ) 
    + group_rank(-(close - open) / open, subindustry), 
    10
)
```

---

## 4. Pairwise Correlation Matrix vs Active Submitted Portfolio

| Submitted Alpha ID | Model Family / Strategy Core | Daily Return Pearson Corr | Daily Return Spearman Corr | Compliance Status |
| :--- | :--- | :--- | :--- | :--- |
| `88pomANl` | Triad PCR 270d + Asset Turn + Intraday | **0.5686** | 0.5072 | **PASS (< 0.70)** |
| `bldOZEjr` | Sales to EV Yield | **0.5512** | 0.5458 | **PASS (< 0.70)** |
| `RR1bxvea` | Asset Turnover Reversion | **0.5443** | 0.5074 | **PASS (< 0.70)** |
| `6Xpn9V2L` | Asset Turnover + Vol Arb Backfilled | **0.5400** | 0.5275 | **PASS (< 0.70)** |
| `e7x3P7gO` | Target Price Premium | **0.4357** | 0.3547 | **PASS (< 0.70)** |
| `78z9d2d5` | Dual Skew Convexity | **0.4166** | 0.3766 | **PASS (< 0.70)** |
| `3qpd8ee6` | Kakushadze IV Alpha #40 Hybrid | **0.2811** | 0.2872 | **PASS (< 0.70)** |
| `2rpzj59P` | Triple-Momentum Vol Regulated | **0.2540** | 0.2464 | **PASS (< 0.70)** |
| `le3WZmdl` | Analyst Overpriced Sentiment | **0.2043** | 0.1864 | **PASS (< 0.70)** |
| `d5RaEvVj` | Intraday Mean Reversion | **0.1837** | 0.1676 | **PASS (< 0.70)** |
| `ZYKo6R78` | Cash Flow Momentum | **0.0385** | -0.0031 | **PASS (< 0.70)** |
| `Jjv1g3xO` | Implied Volatility Spread | **0.0367** | -0.0175 | **PASS (< 0.70)** |

**Maximum Portfolio Correlation**: **`0.5686`** (Exceptional portfolio diversification!).
