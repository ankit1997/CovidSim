import pandas as pd

n = 4

REGIONS = pd.DataFrame({
	'region_id': range(n),
	'region_name': ['USA', 'India', 'Canada', 'UK'],
	
    'travel_dom': [1.0] * n,
    'travel_int': [0.001] * n,
    'domestic_travel_step': [2.0] * n,

	'xmin': [0, 120, 0, 120],
	'xmax': [100, 220, 100, 220],
	'ymin': [0, 0, 120, 120],
	'ymax': [100, 100, 220, 220],

    'quarantine': [0.0] * n,
	'infection_radius': [1.0] * n,
	'prob_of_spread': [0.2] * n

})