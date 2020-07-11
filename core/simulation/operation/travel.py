from numba import njit
from numpy import arange
from random import random, shuffle, normalvariate

@njit
def travel(people, regions):

    home_region_id, region_id, x, y, alive = people[:, 0], people[:, 1], people[:, 2], people[:, 3], people[:, 4]
    r_region_id, r_xmin, r_xmax, r_ymin, r_ymax, r_travel_dom, r_travel_int_in, r_travel_int_out, r_step = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3], regions[:, 4], regions[:, 5], regions[:, 6], regions[:, 7], regions[:, 8]

    idx = arange(regions.shape[0])
    
    for i in range(people.shape[0]):
        
        # find properties of current region
        for r in range(regions.shape[0]):
            if region_id[i] == r_region_id[r]:
                break
        
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

                # found new region which accepted person i
                if home_region_id[i] != r_region_id[idx[j]] and r_travel_int_in[idx[j]] > random():

                    # update to random position inside new region
                    x[i] = random() * (r_xmax[idx[j]] - r_xmin[idx[j]]) + r_xmin[idx[j]]
                    y[i] = random() * (r_ymax[idx[j]] - r_ymin[idx[j]]) + r_ymin[idx[j]]
                    region_id[i] = r_region_id[idx[j]]

                    break
                    
    return x, y, region_id