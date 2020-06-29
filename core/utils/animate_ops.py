import numba
import numpy as np

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
def get_colors(alive, infection):
    colors = np.empty((alive.shape[0], 3))

    for i in range(colors.shape[0]):
        if alive[i] == 0:
            colors[i] = [0.164, 0.2039, 0.349] #2A3459
        elif infection[i] > 0.0 and infection[i] < 0.4:
            colors[i] = [1.0, 1.0, 0.0]
        elif infection[i] >= 0.4:
            colors[i] = [1.0, 0.0, 0.0]
        else:
            colors[i] = [0.03, 0.96, 0.99]
    
    return colors