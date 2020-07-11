from numba import njit

@njit
def social_distancing(people, regions):
    # apply social distancing through pretty dump repel force

    x, y, alive, region_id = people[:, 0], people[:, 1], people[:, 2], people[:, 3]
    r_region_id, r_xmin, r_xmax, r_ymin, r_ymax, r_social_dist = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3], regions[:, 4], regions[:, 5]

    K = 100.0

    # loop through all regions and apply social distancing
    for r in range(regions.shape[0]):

        n_iter = int(r_social_dist[r] * 100)
        xm, xM, ym, yM = r_xmin[r], r_xmax[r], r_ymin[r], r_ymax[r] # region's bounding box

        # keep looping multiple times based on social distancing factor to maximize distance between 2 people
        for _ in range(n_iter):

            # calculate the force exerted on person i by localites
            for i in range(people.shape[0]):
                
                # person should be alive and belong to the region `r` under consideration
                if alive[i] == 0.0 or region_id[i] != r_region_id[r]:
                    continue
                
                # change in (x, y)
                delta_x, delta_y = 0.0, 0.0
                
                # loop through all other people in same region
                for j in range(people.shape[0]):

                    # person `j` should be alive, in same region as that of person `i` and must not be equal to `i`
                    if region_id[i] != region_id[j] or alive[j] == 0.0 or i == j:
                        continue

                    # calculate distance between i and j
                    dist_ij = (x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2

                    # calculate direction of force (for super position)
                    delta_x = delta_x + ( K * ( x[i] - x[j] ) ) / ( dist_ij**2 + 0.0000001 )
                    delta_y = delta_y + ( K * ( y[i] - y[j] ) ) / ( dist_ij**2 + 0.0000001 )
                
                # get new position of persion i
                x[i] = x[i] + delta_x
                y[i] = y[i] + delta_y

                # clip values within the region's bounding box
                x[i] = xm if x[i] < xm else (xM if x[i] > xM else x[i])
                y[i] = ym if y[i] < ym else (yM if y[i] > yM else y[i])
                
    return x, y