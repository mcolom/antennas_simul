#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# %load_ext autoreload
# %autoreload 2

from collections import OrderedDict
import numpy as np
import scipy
import scipy.ndimage.filters
import scipy.signal

freq2key = lambda freq : tuple(np.round(np.multiply(freq, 1e6)).astype(int))
key2freq = lambda key : np.multiply(key, 1.0e-6)

def load_spatial(filename):
    '''
    Load the given filename with the antennas spatial configuration
    '''
    points_spatial = set()

    with open(filename) as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        line_split = line.split(",")

        x = float(line_split[0])
        y = float(line_split[1])

        points_spatial.add((x, y))
    return np.array(list(points_spatial))

def get_min_max(coords):
    '''
    Get the min and max of each dimension of the given coordinates
    '''
    coords = np.array([c for c in coords])
    if len(coords) == 0:
        return None, None, None, None
    return np.min(coords[:, 0]), np.max(coords[:, 0]), \
           np.min(coords[:, 1]), np.max(coords[:, 1])

def get_baselines_dict(points_spatial):
    '''
    Compute all baselines and their multiplicities
    '''
    all_baselines = [np.subtract(p,q) for p in points_spatial for q in points_spatial]
    all_keys = freq2key(all_baselines)

    baselines_dict = OrderedDict()
    for key in all_keys:
        key = tuple(key)

        try:
            baselines_dict[key] += 1
        except KeyError:
            baselines_dict[key] = 1
    return baselines_dict
