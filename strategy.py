"""MNQ intraday momentum, $300 risk at entry (variant of v31n-3 F1).

Signal (Gao-Han-Li-Zhou intraday momentum): sign(09:59 CT close - 17:00 CT
session open), decided at 10:00 CT, filled 10:01 CT open, flat at 15:09 CT.
Regime filter: lagged 20-session mean range > lagged 120-session mean
(exp022: edge lives in high-vol trend regimes).
Risk: 3 MNQ with $300 close-based position stop => risk at entry $300
(gap/slippage risk excepted). Dev evidence: edge concentrated 2020/2022;
absent in NQ/ES 2010-2018 (exp022).
"""
import numpy as np

QTY, STOP, PV = 3, 300.0, 2.0
FAST, SLOW = 20, 120  # trade only if lagged fast mean daily range > lagged slow mean
ENTRY = 86400 + 36060       # 10:01 CT, session-relative clock (17:00 CT = 61200)
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
        o, c = df.open.to_numpy(), df.close.to_numpy()
        n = len(df)
        h, l = df.high.to_numpy(), df.low.to_numpy()
        rng = []  # completed prior sessions' full-session ranges
        starts = np.flatnonzero(np.r_[True, session[1:] != session[:-1]])
        ends = np.r_[starts[1:], n]
        for st, en in zip(starts, ends):
            hot = len(rng) >= SLOW and np.mean(rng[-FAST:]) > np.mean(rng[-SLOW:])
            rng.append(h[st:en].max() - l[st:en].min())  # used only by later sessions
            j = st + np.searchsorted(t[st:en], ENTRY)
            if j - 2 < st or j - 1 >= en:
                continue
            if j == en and t[en - 1] != ENTRY - 60:
                continue  # truncated before decision bar
            base, reference = c[j - 2], o[st]
            if base == reference or not hot:
                continue
            qty = QTY if base > reference else -QTY
            if j == en:
                out[j - 1] = qty
                continue
            e = st + np.searchsorted(t[st:en], EXIT)
            out[j - 1:en] = qty
            if e < en:
                out[e - 1:en] = 0
            basis = o[j]
            for i in range(j, min(e, en) - 1):
                if qty * (c[i] - basis) * PV <= -STOP:
                    out[i:en] = 0
                    break
        result[symbol] = out
    return result
