# -*- coding: utf-8 -*-
from pandas import DataFrame
from pandas_ta import Imports
from pandas_ta.overlap import ma
from pandas_ta.utils import get_offset, non_zero_range, tal_ma, verify_series


def stochf(high, low, close, k=None, d=None, mamode=None, talib=None, offset=None, **kwargs):
    """Fast Stochastic (STOCHF)

    The Fast Stochastic Oscillator (STOCHF) was developed by George Lane in the
    1950's. This STOCHF is more volatile than STOCH (help(ta.stoch)) and it's
    calculation is similar to STOCH.

    Sources:
        https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=333&Name=KD_-_Fast
        https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/fast-stochastic-indicator/

    Calculation:
        Default Inputs:
            k=14, d=3, mamode="sma",
        SMA = Simple Moving Average
        LL  = low for last k periods
        HH  = high for last k periods

        STOCHFk = 100 * (close - LL) / (HH - LL)
        STOCHFd = MA(SMA, STOCH, d)

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        k (int): The Fast %K period. Default: 14
        d (int): The Slow %D period. Default: 3
        mamode (str): See ```help(ta.ma)```. Default: 'sma'
        talib (bool): If TA Lib is installed and talib is True, Returns the TA Lib
            version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        fill_method (value, optional): Type of fill method

    Returns:
        pd.DataFrame: Fast %K, %D columns.
    """
    # Validate arguments
    k = k if k and k > 0 else 14
    d = d if d and d > 0 else 3
    _length = max(k, d)
    high = verify_series(high, _length)
    low = verify_series(low, _length)
    close = verify_series(close, _length)
    offset = get_offset(offset)
    mamode = mamode if isinstance(mamode, str) else "sma"
    mode_tal = bool(talib) if isinstance(talib, bool) else True

    if high is None or low is None or close is None: return

    # Calculate Result
    if Imports["talib"] and mode_tal:
        from talib import STOCHF
        stochf_ = STOCHF(high, low, close, k, d, tal_ma(mamode))
        stochf_k, stochf_d = stochf_[0], stochf_[1]
    else:
        lowest_low = low.rolling(k).min()
        highest_high = high.rolling(k).max()

        stochf_k = 100 * (close - lowest_low)
        stochf_k /= non_zero_range(highest_high, lowest_low)
        stochf_d = ma(mamode, stochf_k.loc[stochf_k.first_valid_index():,], length=d)

    # Offset
    if offset != 0:
        stochf_k = stochf_k.shift(offset)
        stochf_d = stochf_d.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        stochf_k.fillna(kwargs["fillna"], inplace=True)
        stochf_d.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        stochf_k.fillna(method=kwargs["fill_method"], inplace=True)
        stochf_d.fillna(method=kwargs["fill_method"], inplace=True)

    # Name and Categorize it
    _name = "STOCHF"
    _props = f"_{k}_{d}"
    stochf_k.name = f"{_name}k{_props}"
    stochf_d.name = f"{_name}d{_props}"
    stochf_k.category = stochf_d.category = "momentum"

    # Prepare DataFrame to return
    data = {stochf_k.name: stochf_k, stochf_d.name: stochf_d}
    df = DataFrame(data, index=close.index)
    df.name = f"{_name}{_props}"
    df.category = stochf_k.category
    return df