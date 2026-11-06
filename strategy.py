"""Overnight equity risk premium: long MNQ 17:00 -> 06:00 CT.

Screens (exp009/016): MNQ 17-06 CT drift ~ +$9/contract vs $4.25 stressed cost;
06:00-08:29 window negative, so excluded. Causal guards:
- trade only if prior session's 17-06 window had >=95% of minutes (no gap churn);
- after any intra-night missing minute, stay flat rest of night (evaluator
  already flattened; re-entry would pay another round trip);
- stop = lagged 20-session mean 17-06 range; qty = floor($300 / stop$), cap 10.
"""
import numpy as np

RISK, PV, LOOKBACK, CAP, WINDOW_MIN = 300.0, 2.0, 20, 10, 780


def in_night(sec):
    return (sec >= 61200) | (sec < 21540)  # 17:00 .. 05:58 bar; 05:59 bar -> flat


def signals(panel):
    result = {}
    for symbol, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if symbol == "MNQ":
            high, low, close = df.high.to_numpy(), df.low.to_numpy(), df.close.to_numpy()
            sec = df.ct_sec.to_numpy()
            ns = df.index.as_unit("ns").asi8
            ranges, dense_prev = [], False
            for idx in df.groupby("session", sort=False).indices.values():
                night = idx[in_night(sec[idx])]
                stop = np.mean(ranges[-LOOKBACK:]) if len(ranges) >= LOOKBACK else 0.0
                qty = min(CAP, int(RISK / (stop * PV))) if stop > 0 else 0
                if qty and dense_prev and len(night):
                    entry = None
                    for k, i in enumerate(night):
                        if k and ns[i] - ns[night[k - 1]] != 60_000_000_000:
                            break
                        if entry is None:
                            entry = close[i]
                        if close[i] <= entry - stop:
                            break
                        out[i] = qty
                if len(night):
                    ranges.append(high[night].max() - low[night].min())
                dense_prev = len(night) >= 0.95 * WINDOW_MIN
        result[symbol] = out
    return result
