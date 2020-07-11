from numba import njit
from random import random

@njit
def spread_infections(people, regions):

    x, y, alive, infection, region_id = people[:, 0], people[:, 1], people[:, 2], people[:, 3], people[:, 4]
    r_region_id, r_prob_spread, r_infection_radius = regions[:, 0], regions[:, 1], regions[:, 2]

    for i in range(people.shape[0]): # infectant
        if alive[i] == 0 or infection[i] == 0.0: # valid infectant is alive and has infection
            continue

        # get region properties - infection radius and probability of spread
        radius, prob = -1.0, -1.0
        for j in range(regions.shape[0]):
            if r_region_id[j] == region_id[i]:
                radius = r_infection_radius[j]
                prob = r_prob_spread[j]
                break
        
        for j in range(people.shape[0]): # infectee

            if alive[j] == 0 or infection[j] > 0.0: # valid infectee is alive and doesn't have infection
                continue
            
            if ((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2) <= radius ** 2 and random() <= prob:
                # infection can spread (with some probability) if uninfected people (j) are in close proximity with infected people (i)
                infection[j] = min(infection[j] + 0.01, 1.0)

    return infection

@njit
def change_severity(alive, infection):

    for i in range(alive.shape[0]):

        # for people with small signs of infection, a small change that its common flu and will heal automatically
        # TODO: parameterize this value
        # if alive[i] > 0 and infection[i] < 0.2 and random() < 0.1:
        # 	infection[i] /= 2.0
        
        if alive[i] > 0 and infection[i] > 0.0 and infection[i] < 1.0:
            infection[i] = min(infection[i] + 0.01, 1.0)
        
        if alive[i] > 0 and infection[i] == 1.0:
            alive[i] = 0
        
    
    return alive, infection