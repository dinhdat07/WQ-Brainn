# Successful Model: j26Z0d2E (Kakushadze_OrderFlow)
- **Phase**: 14 (Order Flow Imbalance & Microstructure Reversal)
- **Expression**: `ts_decay_linear(rank(vwap - close) * rank(volume / adv20), 10)`
- **Stats**: Sharpe: 1.60 | Fit: 1.01 | Turnover: 19.3%
- **Status**: OUT_OF_SAMPLE (ACTIVE)

## Description
This model is a targeted adaptation of Zura Kakushadze's legendary 101 Formulaic Alphas (Alpha #42). It captures short-term institutional liquidity provision and microstructure mean reversion by analyzing the intra-day volume weighted average price (VWAP) relative to the closing price.

When `vwap > close`, it implies that the stock experienced selling pressure into the close, driving the closing price below its intra-day average. The model multiplies the cross-sectional rank of this pressure by the cross-sectional rank of abnormal volume (`volume / adv20`). The multiplication of ranks ensures a perfectly scaled signal that aggressively buys stocks that crashed hard into the close on unusually high volume (a classic liquidity absorption signature that often reverts the next morning).

## Breakthrough in Uniqueness
This alpha represents a major breakthrough for Phase 14's uniqueness challenge. By strictly utilizing microstructure price-volume relationships without relying on generic statistical z-scores or moving average crossovers, it achieved a maximum correlation of only **+0.2904** against our existing suite of 14 OS alphas. This corresponds to an effective Uniqueness Score of **0.71**, completely bypassing the 0.70 correlation bottleneck.
