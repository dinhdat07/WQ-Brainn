# Successful Model: MPGQwJEn (Distress_Panic_Volume_Reversal)
- **Phase**: 14 (Credit Stress & Short-term Reversal)
- **Expression**: `ts_decay_linear(group_rank((debt - working_capital) / (assets + 1), subindustry) * group_rank(-ts_delta(close, 5), subindustry) * rank(volume / adv20), 10)`
- **Stats**: Sharpe: 1.50 | Fit: 1.25 | Turnover: 10.9%
- **Status**: OUT_OF_SAMPLE (ACTIVE)

## Description
This model identifies severely distressed companies (high debt relative to working capital) that have just experienced a sharp 5-day price drop (-`ts_delta(close, 5)`) accompanied by panic selling volume (`volume / adv20`). 

By multiplying the ranks of these three distinct signals:
1. **Credit Stress**: `group_rank((debt - working_capital) / (assets + 1))`
2. **Crash Reversal**: `group_rank(-ts_delta(close, 5))`
3. **Liquidity Spike**: `rank(volume / adv20)`

We isolate extreme capitulation events. The distressed nature of the company explains *why* the market panics so aggressively. However, the surge in volume indicates that institutional liquidity providers are stepping in to absorb the selling pressure. This sets up a powerful short-term rebound.

## Breakthrough in Uniqueness
In previous iterations, simple distress reversals struggled to pass the `SUB_UNIVERSE_SHARPE` threshold (a measure of robustness across different market caps/regions). By incorporating the `rank(volume / adv20)` multiplier, the signal strength was magnified, pushing the overall Sharpe to 1.50 and Fitness to 1.25. The model achieved a max correlation of **+0.6441** (vs `bldOZEjr`), successfully staying below the strict 0.70 limit, making it our 16th actively surviving alpha.
