from numba import njit
from numpy import arange
from random import random, shuffle, normalvariate

'''
    Move people around.
    Arguments:
        people:
            (home region_id, region_id, x, y, alive)
        regions:
            (region_id, xmin, xmax, ymin, ymax, Domestic travel factor, Incoming travellers, Outgoing travellers, step size for domestic travel)
    Returns:
        (x, y, region_id) : new positions and regions
'''
@njit
def travel(people, regions):

    # get values from arguments
    home_region_id, region_id, x, y, alive = people[:, 0], people[:, 1], people[:, 2], people[:, 3], people[:, 4]
    r_region_id, r_xmin, r_xmax, r_ymin, r_ymax, r_travel_dom, r_travel_int_in, r_travel_int_out, r_step = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3], regions[:, 4], regions[:, 5], regions[:, 6], regions[:, 7], regions[:, 8]

    # region index (used for internation travel selection)
    idx = arange(regions.shape[0])
    
    # loop through all people
    for i in range(people.shape[0]):
        
        # find properties of current region - r
        for r in range(regions.shape[0]):
            if region_id[i] == r_region_id[r]:
                break # r will be the index of current region
        
        # domestic travel
        if alive[i] > 0 and r_travel_dom[r] > random():

            # find out bounds of current region and step size for domestic travel
            xm, xM, ym, yM, step = r_xmin[r], r_xmax[r], r_ymin[r], r_ymax[r], r_step[r]
            
            # travel within step size 
            x[i] = x[i] + normalvariate(0.0, step)
            y[i] = y[i] + normalvariate(0.0, step)

            # clip position to within bounding box
            x[i] = xm if x[i] < xm else (xM if x[i] > xM else x[i])
            y[i] = ym if y[i] < ym else (yM if y[i] > yM else y[i])
        
        # international travel
        if alive[i] > 0 and r_travel_int_out[r] > random():

            # shuffle international destinations
            shuffle(idx)
            
            # find new region to go to
            for j in range(len(idx)):
                
                j_region_id = r_region_id[idx[j]]
                j_acceptance = r_travel_int_in[idx[j]]
                j_xmin, j_xmax, j_ymin, j_ymax = r_xmin[idx[j]], r_xmax[idx[j]], r_ymin[idx[j]], r_ymax[idx[j]]

                # found new region which accepted person i
                if home_region_id[i] != j_region_id and j_acceptance > random():

                    # update to random position inside new region
                    x[i] = random() * (j_xmax - j_xmin) + j_xmin
                    y[i] = random() * (j_ymax - j_ymin) + j_ymin
                    region_id[i] = j_region_id
                    break
    
    # return new coordinates and region ids
    return x, y, region_id