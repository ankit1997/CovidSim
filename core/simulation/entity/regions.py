import pandas as pd

# list of regions
region_names = ['USA', 'India', 'Canada', 'UK', 'China', 'Australia', 'Germany', 'Italy']

# number of regions
n = len(region_names)

REGIONS = pd.DataFrame({
	'region_id': range(n),
	'region_name': region_names,
	
    'travel_dom': [0.7] * n, # allowing people to move within the region
    'travel_int_in': [0.05] * n, # allowing international travellers in the region
	'travel_int_out': [0.01] * n, # allowing people in the region to travel internationally
    'domestic_travel_step': [2.0] * n, # travel step size - for domestic travel

	'xmin': [0, 150, 300, 450, 0, 150, 300, 450],
	'xmax': [100, 250, 400, 550, 100, 250, 400, 550],
	'ymin': [0, 0, 0, 0, 150, 150, 150, 150],
	'ymax': [100, 100, 100, 100, 250, 250, 250, 250],

    'social_distancing': [0.01] * n,
	'infection_radius': [2.0] * n,
	'prob_of_spread': [0.2] * n,
	'visible_infection': [0.4] * n,

	'funds': [1e9] * n,	# initial funds allocated per region

})