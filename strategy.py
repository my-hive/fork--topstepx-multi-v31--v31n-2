"""Causal MBT impulse-reversal research candidate; one micro contract."""
import numpy as np


def signals(panel):
    result = {}
    for symbol, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if symbol == "MBT":
            for indices in df.groupby("session", sort=False).indices.values():
                close = df.close.to_numpy()[indices]
                sec = df.ct_sec.to_numpy()[indices]
                returns = np.zeros(len(close), dtype=float)
                if len(close) > 60:
                    returns[60:] = close[60:] / close[:-60] - 1.0
                position = 0
                age = 0
                stop = 0.0
                for j in range(60, len(close)):
                    if position:
                        age += 1
                        adverse = close[j] <= stop if position > 0 else close[j] >= stop
                        if age >= 15 or adverse or sec[j] >= 52200:
                            position = 0
                    elif 27000 <= sec[j] < 50400 and abs(returns[j]) >= 0.01:
                        position = -int(np.sign(returns[j]))
                        age = 0
                        stop = close[j] * (0.98 if position > 0 else 1.02)
                    out[indices[j]] = position
        result[symbol] = out
    return result
