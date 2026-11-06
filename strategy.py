"""Overnight equity risk-premium sleeve: long MNQ 17:00 CT -> 08:29 CT.

Stop = 0.6 x lagged 20-session mean overnight range; size = floor($300 / stop$).
Risk per trade <= $300 by construction (gap risk excepted).
"""
import numpy as np

RISK, PV, STOP_K, LOOKBACK = 300.0, 2.0, 0.6, 20


def signals(panel):
    result = {}
    for symbol, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if symbol == "MNQ":
            high, low, close = df.high.to_numpy(), df.low.to_numpy(), df.close.to_numpy()
            sec = df.ct_sec.to_numpy()
            ranges = []  # completed prior sessions' overnight ranges only
            for idx in df.groupby("session", sort=False).indices.values():
                s = sec[idx]
                night = idx[(s >= 61200) | (s < 30600)]
                stop = np.mean(ranges[-LOOKBACK:]) * STOP_K if len(ranges) >= LOOKBACK else 0.0
                qty = min(50, int(RISK / (stop * PV))) if stop > 0 else 0
                if qty and len(night):
                    entry, pos = None, qty
                    for i in night:
                        if 30540 <= sec[i] < 61200:  # 08:29 bar: target flat
                            break
                        if entry is None:
                            entry = close[i]
                        if close[i] <= entry - stop:
                            break
                        out[i] = pos
                if len(night):
                    ranges.append(high[night].max() - low[night].min())
        result[symbol] = out
    return result
