import pandas as pd
import numpy as np


def calculate_atr(df, lookback=14):
    """Calculates Average True Range (ATR)."""
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())

    true_range = np.maximum.reduce([high_low, high_close, low_close])
    true_range_series = pd.Series(true_range, index=df.index)
    return true_range_series.rolling(window=lookback, min_periods=1).mean()
