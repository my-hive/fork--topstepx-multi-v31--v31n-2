"""MNQ intraday momentum, $300 risk-at-entry compliant (derived from v31n-3 F1).

Signal (Gao-Han-Li-Zhou intraday momentum): sign(09:59 CT close - 17:00 CT
session open), decided at 10:00 CT, filled 10:01 CT, flat 15:09 CT.
Risk: close-based stop distance = 0.5 x lagged 20-session mean of the
10:01-15:09 high-low range (prior sessions only); qty = floor($300 / stop$),
capped at 10 MNQ. Stop$ x qty <= $300 at entry (gap risk excepted).
"""
import numpy as np

RISK, PV, K, LOOKBACK, CAP = 300.0, 2.0, 0.5, 20, 10
ENTRY = 86400 + 36060       # 10:01 CT, session-relative clock
EXIT = 86400 + 54540        # 15:09 CT bar


def signals(panel):
    result = {}
    for symbol, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if symbol != "MNQ":
            result[symbol] = out
            continue
        sec = df.ct_sec.to_numpy().astype(np.int64)
        t = np.where(sec >= 61200, sec, sec + 86400)
        session = df.session.to_numpy()
        o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
        n = len(df)
        starts = np.flatnonzero(np.r_[True, session[1:] != session[:-1]])
        ends = np.r_[starts[1:], n]
        ranges = []  # completed prior sessions' 10:01-15:09 ranges
        for st, en in zip(starts, ends):
            j = st + np.searchsorted(t[st:en], ENTRY)
            e = st + np.searchsorted(t[st:en], EXIT)
            stop = K * np.mean(ranges[-LOOKBACK:]) if len(ranges) >= LOOKBACK else 0.0
            if e < en and e > j:  # session complete through 15:09: record range for later sessions
                ranges.append(h[j:e].max() - l[j:e].min())
            if not stop or j - 2 < st or j - 1 >= en:
                continue
            if j == en and t[en - 1] != ENTRY - 60:
                continue
            base, reference = c[j - 2], o[st]
            qty = min(CAP, int(RISK / (stop * PV)))
            if base == reference or not qty:
                continue
            qty = qty if base > reference else -qty
            if j == en:
                out[j - 1] = qty
                continue
            out[j - 1:en] = qty
            if e < en:
                out[e - 1:en] = 0
            basis = o[j]
            for i in range(j, min(e, en) - 1):
                if np.sign(qty) * (c[i] - basis) <= -stop:
                    out[i:en] = 0
                    break
        result[symbol] = out
    return result
