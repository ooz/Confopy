# coding: utf-8
'''
File: statistics.py
Author: Oliver Zscheyge
Description:
    Collection of statistics functions.
'''

import math



def mean(values, ndigits=None):
    """
    Return:
        Mean of values, rounded to ndigits.
    """
    n = len(values)
    if n == 0:
        raise ValueError(u"Can't compute mean over empty list!")
    su = math.fsum(values)
    if ndigits is not None:
        return round(su / float(n), ndigits)
    return su / float(n)

def variance(values, ndigits=None):
    """
    Args:
        values: List of at least 2 values.
    Return:
        Variance of a list of values, rounded to ndigits.
    """
    n = len(values)
    if n < 2:
        raise ValueError(u"Can't compute variance over less than 2 values.")
    mean = math.fsum(values) / float(n)
    var = math.fsum([(v - mean) * (v - mean) for v in values])
    if ndigits is not None:
        return round(var / float(n), ndigits)
    return var / float(n)

def stdev(values, ndigits=None):
    """
    Args:
        values: List of at least 2 values.
    Return:
        Standard deviation of a list of values, rounded to ndigits.
    """
    n = len(values)
    if n < 2:
        raise ValueError(u"Can't compute standard deviation over less than 2 values.")
    mean = math.fsum(values) / float(n)
    var = math.fsum([(v - mean) * (v - mean) for v in values]) / float(n)
    if ndigits is not None:
        return round(math.sqrt(var), ndigits)
    return math.sqrt(var)

def mean_stdev(values, ndigits=None):
    """
    Args:
        values: List of at least 2 values.
    Return:
        (mean, standard deviation) tuple of a list of values, rounded to ndigits.
    """
    n = len(values)
    if n < 2:
        raise ValueError(u"Can't compute variance/standard deviation over less than 2 values.")
    mean = math.fsum(values) / float(n)
    sd = math.sqrt(math.fsum([(v - mean) * (v - mean) for v in values]) / float(n))
    if ndigits is not None:
        return (round(mean, ndigits), round(sd, ndigits))
    return (mean, sd)



if __name__ == '__main__':
    print u"TestCase for %s..." % __file__
    values = range(10)
    mean = mean(values)
    assert mean == 4.5
    var = variance(values)
    assert var == 8.25
    stdev = stdev(values)
    assert stdev == math.sqrt(var)
    (mean2, stdev2) = mean_stdev(values)
    assert mean == mean2
    assert stdev == stdev2
    stats_rounded = mean_stdev(values, 2)
    assert stats_rounded == (4.5, 2.87)
    print u"...all asserts passed!"


