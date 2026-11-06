# v31n-2 mechanism notes (DEVELOPMENT evidence only)

## Rejected (30 recorded experiments, see experiments.jsonl)
- MBT 60m impulse fade/continuation: gross ~0 before costs (exp005-006).
- Scheduled news drift (EIA crude, 07:30 macro, NG storage, USDA 11:00): none (exp007/013/018).
- 51-root late-day momentum, 20d TSMOM, turn-of-month: real signs, all below 2-tick stressed cost (exp008/014/015).
- FX WM/R 16:00 London fix reversal: broad (6J t=3.6) but $3-10/ct vs $27-57 cost (exp012).
- Overnight equity premium: real (NQ 20:00-01:00 CT t=2.0) but below cost; MNQ sleeve -$2.3k (exp009/016/017).
- Evaluator lesson: persistent targets in sparse markets re-enter after each gap flatten (M6E 89k entries).

## Finalists: MNQ intraday momentum (v31n-3 F1 signal, reproduced exp019 at 0.2307)
F1 holds 5 MNQ with an $800 stop, so its risk at entry is $800, above the program's $300 per-trade cap. These variants keep risk at or below $300:
| ID | SHA256 prefix | change | score | null p | PnL | +ticks to b/e |
|---|---|---|---|---|---|---|
| A | 71099801 | 3 MNQ, $300 stop | 0.1337 | 0.015 | +13,985 | 3.8 |
| C | 994fd36e | A + lagged 20>120 range regime gate | 0.0770 | 0.005 | +14,909 | 10.9 |
| B | 69c5b6f3 | A + skip |move|<0.5x lagged mean | 0.0757 | 0.020 | +20,575 | 8.8 |

Caveat: there is no edge in NQ/ES from 2010-2018 (exp022). The development edge comes from 2020 and 2022, so it is regime-dependent. A, B, and C use one shared signal. They are not independent evidence. A development score does not show deployable profit.
