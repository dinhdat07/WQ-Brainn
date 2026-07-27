
### Batch 19 - Phase 6: Volatility & Liquidity Anomalies
1. 19_1_Amihud_Premium: ZYKalgYn | Sharpe: -0.91 | Fit: -0.4 | TO: 0.2511
2. 19_2_Low_Vol_Anomaly: ERROR (ts_stddev inaccessible)
3. 19_3_Amihud_Reversion: YPgak32R | Sharpe: 0.08 | Fit: 0.01 | TO: 0.3048
4. 19_4_Vol_Adj_Reversion: ERROR (ts_stddev inaccessible)
5. 19_5_Vol_Surprise_Rev: kqZaLd2O | Sharpe: 2.23 | Fit: 0.98 | TO: 0.7606
6. 19_6_High_Low_Rev: zqRdJXVX | Sharpe: 1.89 | Fit: 0.74 | TO: 0.7585
7. 19_7_Intraday_Rev: MPL65bQ9 | Sharpe: 1.88 | Fit: 0.97 | TO: 0.7486
8. 19_8_Range_Contrarian: ERROR (ts_min inaccessible)
9. 19_9_Vol_Weighted_Rev: d5RalZJv | Sharpe: 1.67 | Fit: 0.83 | TO: 0.7349
10. 19_10_Amihud_5d_Rev: 88eNKNOq | Sharpe: 0.59 | Fit: 0.2 | TO: 0.3262

**Findings**: Excellent predictive power (Sharpe up to 2.23) using Reversion/Price x Volume interactions, bypassing the self-correlation of traditional fundamentals! However, high turnover (~0.75) lowers the fitness below the 1.0 threshold. Solution for next batch: apply higher ts_decay_linear windows to these top models.

### Batch 20 - Phase 6: Turnover Reduction via Decay (10, 15, 20)
**Objective**: Drop turnover of 4 best Phase 6 models below 0.6 to push fitness > 1.0.

- Model 1 (Vol Surprise Rev D10): vRvAJQLA | Sharpe 2.02 | Fit 1.0 | TO 0.5567
- Model 2 (Vol Surprise Rev D15): 9q7la18K | Sharpe 1.82 | Fit 0.94 | TO 0.461
- Model 3 (Vol Surprise Rev D20): 88eNagYq | Sharpe 1.68 | Fit 0.9 | TO 0.4037
- Model 4 (High Low Rev D10): 0mMPe7W1 | Sharpe 1.88 | Fit 0.88 | TO 0.5527
- Model 5 (High Low Rev D15): 9q7laV9e | Sharpe 1.82 | Fit 0.94 | TO 0.4558
- Model 6 (High Low Rev D20): YPga2lrM | Sharpe 1.69 | Fit 0.91 | TO 0.3971
- **Model 7 (Intraday Rev D10): d5RaEvVj | Sharpe 1.75 | Fit 1.04 | TO 0.5451 [SUCCESS!]**
- Model 8 (Intraday Rev D15): kqZanxwO | Sharpe 1.57 | Fit 0.98 | TO 0.4512
- Model 9 (Intraday Rev D20): 9q7l90mK | Sharpe 1.48 | Fit 0.96 | TO 0.3951
- Model 10 (Vol Weighted Rev D10): P0O5nwGL | Sharpe 1.49 | Fit 0.84 | TO 0.5217
- Model 11 (Vol Weighted Rev D15): P0O5n3Kx | Sharpe 1.32 | Fit 0.77 | TO 0.4258
- Model 12 (Vol Weighted Rev D20): WjVlNYeP | Sharpe 1.24 | Fit 0.76 | TO 0.3698

**Findings**: 	s_decay_linear(10) hit the sweet spot between retaining the signal's explosive Sharpe while crushing turnover below 0.6. d5RaEvVj (Intraday Reversion) passed successfully.
