import pandas as pd

n = 6

REGIONS = pd.DataFrame({
	'region_id': range(n),
	'region_name': ['USA', 'India', 'Canada', 'UK', 'China', 'Australia'],
	
    'travel_dom': [1.0, 1.0, 0.5, 1.0, 1.0, 1.0],
    'travel_int': [0.001, 0.001, 0.001, 0.00001, 0.001, 0.01],
    'domestic_travel_step': [2.0, 2.0, 2.0, 1.0, 1.0, 1.0],

	'xmin': [0, 120, 240, 0, 120, 240],
	'xmax': [100, 220, 340, 100, 220, 340],
	'ymin': [0, 0, 0, 120, 120, 120],
	'ymax': [100, 100, 100, 220, 220, 220],

    'quarantine': [0.0] * n,
	'infection_radius': [5.0] * n,
	'prob_of_spread': [0.2] * n,
	'visible_infection': [0.4] * n

})