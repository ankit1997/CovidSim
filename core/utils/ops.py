import numba
import numpy as np
from random import random, uniform, normalvariate, shuffle

@numba.jit(nopython=True)
def random1D(n):
    result = np.empty((n,))
    for i in range(n):
        result[i] = random()
    return result

@numba.jit(nopython=True)
def random_uniform1D(low, high):
    result = np.empty_like(low)
    for i in range(low.shape[0]):
        result[i] = uniform(low[i], high[i])
    return result

@numba.jit(nopython=True)
def random_normal1D(std):
    result = np.empty_like(std)
    for i in range(std.shape[0]):
        result[i] = normalvariate(0.0, std[i])
    return result

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
def interpolate2D(new, old, t, t0, tn):
    R, C = new.shape
    
    result = np.empty_like(new)
    for i in range(R):
        for j in range(C):
            result[i, j] = (tn-t) * old[i, j] + (t-t0) * new[i, j]
            result[i, j] = result[i, j] / (tn-t0)
    
    return result

@numba.jit(nopython=True)
def travel_international(current_region_index, region_index, xmin, xmax, ymin, ymax):
    new_region_index = []
    x = []
    y = []
    
    region_index_bkp = region_index.copy()
    for i in range(len(current_region_index)):
        region_index_list = region_index_bkp.copy()
        shuffle(region_index_list)

        new_region = region_index_list[0] if region_index_list[0] != current_region_index[i] else region_index_list[1]
        new_region_index.append(new_region)

        for j in range(len(region_index_bkp)):
            if region_index_bkp[j] == new_region:
                x.append(uniform(xmin[j], xmax[j]))
                y.append(uniform(ymin[j], ymax[j]))
    
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
            
            if ((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2) <= radius[i] ** 2:
                # infection can spread if uninfected people (j) are in close proximity with infected people (i)
                if random() <= prob_spread[i]:
                    infectants.append(i)
                    infectees.append(j)
    
    return infectants, infectees