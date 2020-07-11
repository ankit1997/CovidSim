import pandas as pd

MEDICS = pd.DataFrame({
	'medic_id': [],
    'region_id': [],

    'capacity': [],
    'quality': [],
	
    'travel_dom': [1.0] * n,													# allowing people to move within the region
    'travel_int_in': [0.5] * n, 												# allowing international travellers in the region
	'travel_int_out': [0.01] * n,												# allowing people in the region to travel internationally
    'domestic_travel_step': [2.0] * n,											# travel step size - for domestic travel

	'xmin': [0, 150, 300, 0, 150, 300],
	'xmax': [100, 250, 400, 100, 250, 400],
	'ymin': [0, 0, 0, 150, 150, 150],
	'ymax': [100, 100, 100, 250, 250, 250],

    'social_distancing': [0.0] * n,
	'infection_radius': [2.0] * n,
	'prob_of_spread': [0.5] * n,
	'visible_infection': [0.4] * n,

	'funds': [1e9] * n,															# initial funds allocated per region

})