import pandas as pd

n = 6

REGIONS = pd.DataFrame({
	'region_id': range(n),
	'region_name': ['USA', 'India', 'Canada', 'UK', 'China', 'Australia'],
	
    'travel_dom': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    'travel_int': [0.001, 0.001, 0.001, 0.001, 0.001, 0.001],
    'domestic_travel_step': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],

	'xmin': [0, 150, 300, 0, 150, 300],
	'xmax': [100, 250, 400, 100, 250, 400],
	'ymin': [0, 0, 0, 150, 150, 150],
	'ymax': [100, 100, 100, 250, 250, 250],

    'quarantine': [0.0] * n,
	'infection_radius': [3.0] * n,
	'prob_of_spread': [0.2] * n,
	'visible_infection': [0.4] * n,

	'funds': [1e9] * n,

})