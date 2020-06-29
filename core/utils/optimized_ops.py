import numba
import numpy as np
from random import random, shuffle

@numba.jit(nopython=True)
def any1D(bools):
    for i in range(bools.shape[0]):
        if bools[i]:
            return True
    return False

@numba.jit(nopython=True)
def add1D(a, b):
    n = a.shape[0]

    result = np.empty_like(a)
    for i in range(n):
        result[i] = a[i] + b[i]
    
    return result

@numba.jit(nopython=True)
def clip1D(a, low, high):
    n = a.shape[0]

    result = np.empty_like(a)
    for i in range(n):
        if a[i] < low[i]:
            result[i] = low[i]
        elif a[i] > high[i]:
            result[i] = high[i]
        else:
            result[i] = a[i]
    
    return result

@numba.jit(nopython=True)
def travel_international(current_region_index, region_index, xmin, xmax, ymin, ymax):
    new_region_index = np.empty((len(current_region_index),))
    x = np.empty((len(current_region_index),))
    y = np.empty((len(current_region_index),))
    
    region_index_bkp = region_index.copy()
    for i in range(len(current_region_index)):
        region_index_list = region_index_bkp.copy()
        shuffle(region_index_list)

        new_region = region_index_list[0] if region_index_list[0] != current_region_index[i] else region_index_list[1]
        new_region_index[i] = new_region

        for j in range(len(region_index_bkp)):
            if region_index_bkp[j] == new_region:
                x[i] = random() * (xmax[j] - xmin[j]) + xmin[j]
                y[i] = random() * (ymax[j] - ymin[j]) + ymin[j]
                break
    
    return new_region_index, x, y

@numba.jit(nopython=True)
def get_new_infections(x, y, alive, infection, radius, prob_spread):
    n = x.shape[0]
    infectants = []
    infectees = []

    for i in range(n): # infectant
        if alive[i] == 0 or infection[i] == 0.0: # valid infectant is alive and has infection
            continue
        
        for j in range(n): # infectee
            if alive[j] == 0 or infection[j] > 0.0: # valid infectee is alive and doesn't have infection
                continue
            
            if ((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2) <= radius[i] ** 2 and random() <= prob_spread[i]:
                # infection can spread (with some probability) if uninfected people (j) are in close proximity with infected people (i)
                infectants.append(i)
                infectees.append(j)
    
    return infectants, infectees