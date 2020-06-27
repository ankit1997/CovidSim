import numpy as np
import pandas as pd

from core.simulation.people import PEOPLE
from core.simulation.regions import REGIONS
from core.simulation.validator import validate_people, validate_regions


class World(object):

	def __init__(self, num_people=100, T=10):
		self.num_people = num_people
		self.people = PEOPLE
		self.regions = REGIONS
		self.T = T
		self.t = 0

		self.initialize()
		validate_people(self.people)
		validate_regions(self.regions)

	def initialize(self):
		# initialize world dataframe
		print('Initializing a {}x{} world...'.format(len(self.regions), self.num_people))

		num_regions = float(len(self.regions))

		# loop for each region
		for i, region in enumerate(self.regions.region_name):
			# get region window
			xmin, xmax, ymin, ymax = self.regions.loc[i, ['xmin', 'xmax', 'ymin', 'ymax']].values.tolist()
			
			# create region population
			region_population = pd.DataFrame({
				'person_id': range(i*self.num_people+1, i*self.num_people+1+self.num_people),
				'home_region_name': [region] * self.num_people,
				'region_name': [region] * self.num_people,
				'x': (np.random.random(size=(self.num_people, ))) * (xmax-xmin) + xmin,
				'y': (np.random.random(size=(self.num_people, ))) * (ymax-ymin) + ymin,
				'alive': [1] * self.num_people,
				'infection': [0.0] * self.num_people,
			})

			# add region population to world population
			self.people = pd.concat([self.people, region_population], axis=0).reset_index(drop=True)
	
	def simulate(self):
		self.t += 1

		self.move_domestic()
		self.move_international()

		return self.people, self.regions
	
	def move_domestic(self):
		# simulate domestic travel

		# join people and regions
		combined = pd.merge(self.people, self.regions, on='region_name', how='left')

		# get people who will move
		move_idx = (np.random.random((combined.shape[0], )) < combined['travel_dom']) & (combined.loc[:, 'alive'] == 1.0)

		# move people
		move_x = np.random.normal(scale=combined.loc[move_idx, 'domestic_travel_step']).reshape((-1, 1))
		move_y = np.random.normal(scale=combined.loc[move_idx, 'domestic_travel_step']).reshape((-1, 1))
		combined.loc[move_idx, ['x', 'y']] += np.concatenate([move_x, move_y], axis=1)

		# make sure no one leaves boundary while domestic travel
		combined.loc[move_idx, 'x'] = combined.loc[move_idx, 'x'].clip(combined.loc[move_idx, 'xmin'], combined.loc[move_idx, 'xmax'])
		combined.loc[move_idx, 'y'] = combined.loc[move_idx, 'y'].clip(combined.loc[move_idx, 'ymin'], combined.loc[move_idx, 'ymax'])

		# get new people dataframe from movers
		self.people.loc[move_idx, ['x', 'y']] = combined.loc[move_idx, ['x', 'y']]

	def move_international(self):
		# simulate international travel

		# if only one region in simulaton, return as no international travel possible
		if len(self.regions) == 1:
			return

		# join people and regions
		combined = pd.merge(self.people, self.regions, on='region_name', how='left')

		# get people who will move
		move_idx = (np.random.random((combined.shape[0], )) < combined['travel_int']) & (combined.loc[:, 'alive'] == 1.0)

		if np.count_nonzero(move_idx) == 0:
			return
		
		# update region name of movers to new random region
		combined.loc[move_idx, 'region_name'] = combined.loc[move_idx, 'region_name'].apply(
			lambda region: self.regions[self.regions.region_name != region].region_name.sample(n=1).item()
		)
		
		# get new location of movers
		movers_comb = combined.loc[move_idx, ['region_name', 'x', 'y']].merge(self.regions, on='region_name', how='left').set_index(combined.loc[move_idx, :].index)
		movers_comb.loc[:, 'x'] = np.random.uniform(movers_comb.xmin, movers_comb.xmax)
		movers_comb.loc[:, 'y'] = np.random.uniform(movers_comb.ymin, movers_comb.ymax)

		# update co-ordinates and region name of international travellers
		self.people.loc[move_idx, ['x', 'y', 'region_name']] = movers_comb.loc[:, ['x', 'y', 'region_name']]
	
	def spread_infections(self):
		# infect new people

		for i, region in enumerate(self.regions.region_name):

			# get region population
			local = self.people.loc[self.people.region_name == region, :]
			
			# calculate distances between each person in the region
			Xdiff = (local.x.values[:, None] - local.x.values) ** 2
			Ydiff = (local.y.values[:, None] - local.y.values) ** 2
			# distance is N x N matrix of squared distances between each pair of points
			distance = Xdiff + Ydiff

			# filter distances for infected people only since they'll spread infection
			infected_mask = local.infection > 0.0
			infected_dist = distance[infected_mask]

			# calculate people in threshold distance
			thres = np.argwhere(infected_dist <= (self.regions.loc[i, 'infection_radius'] ** 2))
			thres_infectee = thres[:, 0]                        # already infected people
			thres_infected = thres[:, 1]                        # in threshold distance to infected people

			# index of people who are in threshold distance to infected people and are currently uninfected
			idx = local.loc[thres_infected, 'infection'] == 0.0
			
			infection_creators = thres_infectee[idx]
			candidates = thres_infected[idx]
			
			if candidates.size > 0:
				# get prob that each candidate will get infection
				cand_prob = np.random.random(candidates.shape) <= self.regions.loc[i, 'prob_of_spread']
				
				infection_creators = infection_creators[cand_prob]
				newly_infected = candidates[cand_prob]

				# infect candidates :(
				self.people.loc[newly_infected, 'infection'] = self.people.loc[infection_creators, 'infection']
