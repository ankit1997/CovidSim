import numpy as np

def validate_people(people):
    
    print('Validating people...')
    
    try:
        if np.count_nonzero(people.isna().values) > 0:
            raise ValueError("People's array messed up!")
    except Exception as exp:
        print(exp)
        ans = input('Do you want to continue? [y/n]: ')
        if ans.upper() != 'Y':
            exit()

def validate_regions(regions):
    
    print('Validating regions...')
    
    try:
        n = len(regions)
        
        ## Validate range of column values

        for col in ['travel_dom', 'travel_int_in', 'travel_int_out', 'social_distancing', 'prob_of_spread']:
            if np.count_nonzero((regions.loc[:, col] < 0.0) | (regions.loc[:, col] > 1.0)) > 0:
                raise ValueError("{} values are outside [0, 1]".format(col))
        
        ## Validate if regions overlap

        xmins = regions.xmin.tolist()
        xmaxs = regions.xmax.tolist()
        ymins = regions.ymin.tolist()
        ymaxs = regions.ymax.tolist()

        # check if a point is inside a bounding box
        def is_inside(pt, xmin, xmax, ymin, ymax):
            x, y = pt
            return x >= xmin and x <= xmax and y >= ymin and y <= ymax

        for i in range(n-1):
            # corner points for region i
            pt1 = (xmins[i], ymins[i]) # bottom left
            pt2 = (xmins[i], ymaxs[i]) # top left
            pt3 = (xmaxs[i], ymins[i]) # bottom right
            pt4 = (xmaxs[i], ymaxs[i]) # top right

            for j in range(i+1, n):
                # assert that no corner point of region i should be inside other region j
                assert not(
                    is_inside(pt1, xmins[j], xmaxs[j], ymins[j], ymaxs[j])
                    or is_inside(pt2, xmins[j], xmaxs[j], ymins[j], ymaxs[j])
                    or is_inside(pt3, xmins[j], xmaxs[j], ymins[j], ymaxs[j])
                    or is_inside(pt4, xmins[j], xmaxs[j], ymins[j], ymaxs[j])
                ), "Overlapping regions: {} and {}".format(i, j)
    
    except Exception as exp:
        print(exp)
        ans = input('Do you want to continue? [y/n]: ')
        if ans.upper() != 'Y':
            exit()