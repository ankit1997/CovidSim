from numba import njit
from random import random

'''
    Spread infection around an already infected person.
    Arguments:
        people:
            (x, y, alive, infection, region_id)
        region:
            (region_id, probability of spread, infection radius)
    Return:
        infection - new infection score
'''
@njit
def spread_infections(people, regions):

    # get values from arguments
    x, y, alive, infection, region_id = people[:, 0], people[:, 1], people[:, 2], people[:, 3], people[:, 4]
    r_region_id, r_prob_spread, r_infection_radius = regions[:, 0], regions[:, 1], regions[:, 2]

    # go through all regions
    for r in range(regions.shape[0]):

        for i in range(people.shape[0]): # infectant - one who is infected

            # valid infectant is alive and has infection
            # additionally, consider only infectants of region r
            if alive[i] == 0 or infection[i] == 0.0 or r_region_id[r] != region_id[i]:
                continue
            
            for j in range(people.shape[0]): # infectee - one who gets infected

                # valid infectee is alive and doesn't have infection
                # additionally, consider only infectants of region r
                if alive[j] == 0 or infection[j] > 0.0 or r_region_id[r] != region_id[j]:
                    continue
                
                if ((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2) <= r_infection_radius[r] ** 2 and random() <= r_prob_spread[r]:
                    # infection spread occurs when an uninfected person is in close proximity of infected person
                    # apart from this, there is certain probability the person might not get infection due to factors like personal hygiene etc.
                    infection[j] = min(infection[i] / 4.0, 0.2)

    # return new values of infection
    return infection


'''
    Change the severity of the infection for people who are already infected
    Arguments:
        alive, infection
    Return:
        alive, infection - new alive status and infection score
'''
@njit
def change_severity(alive, infection):

    # go through each person
    for i in range(alive.shape[0]):
        
        # if person is alive and has infection, increase the infection by small degree
        if alive[i] > 0 and infection[i] > 0.0 and infection[i] < 1.0:
            infection[i] = min(infection[i] + 0.01, 1.0)
        
        # RIP for highly severe cases
        if alive[i] > 0 and infection[i] == 1.0:
            alive[i] = 0
        
    # return new alive status and infection score
    return alive, infection