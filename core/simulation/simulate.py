import numpy as np
import pandas as pd
from numba import njit
from random import random, shuffle, normalvariate

from core.simulation.entity.people import PEOPLE
from core.simulation.entity.regions import REGIONS

from core.simulation.operation.travel import travel as travel_op
from core.simulation.operation.spread import spread_infections as spread_op
from core.simulation.operation.spread import change_severity as change_severity_op
from core.simulation.operation.social_distancing import social_distancing as social_distancing_op


class Simulator(object):

	'''
		Simulator class
		Arguments:
			`num_people`: Number of people per region
	'''

	def __init__(self, num_people):
		self.num_people = num_people
		self.people = PEOPLE
		self.regions = REGIONS
		self.T = 0
		self.create_people()
	
	def create_people(self):
		# create people per region

		print('Creating a {}x{} world...'.format(len(self.regions), self.num_people))

		# loop for each region
		for i, region in enumerate(self.regions.region_id):
			
			# get region window
			xmin, xmax, ymin, ymax = self.regions.loc[i, ['xmin', 'xmax', 'ymin', 'ymax']].values.tolist()
			
			# create region population
			region_population = pd.DataFrame({
				'person_id': range(i*self.num_people+1, i*self.num_people+1+self.num_people),
				'home_region_id': [region] * self.num_people,
				'region_id': [region] * self.num_people,
				'x': (np.random.random(size=(self.num_people, ))) * (xmax-xmin) + xmin,
				'y': (np.random.random(size=(self.num_people, ))) * (ymax-ymin) + ymin,
				'alive': [1] * self.num_people,
				'infection': [0.0] * self.num_people,
			})

			# add region population to world population
			self.people = pd.concat([self.people, region_population], axis=0).reset_index(drop=True)
	
	def initialize_infections(self, num_infections=5):
		# set few people with infections
		idx = self.people.sample(n=num_infections).index
		self.people.loc[idx, 'infection'] = 0.1
	
	def set_policy(self, region_id, key, value):
		# update region policy
		self.regions.loc[self.regions.region_id == region_id, key] = value
	
	def get_SIR(self):
		return self._get_SIR(
			self.people.loc[:, ['region_id', 'alive', 'infection']].values,
			self.regions.loc[:, ['region_id', 'xmax', 'ymin', 'ymax', 'visible_infection']].values
		)
	
	def call(self):

		# current timestep
		self.T += 1

		# travel people around
		self.people.loc[:, 'x'], self.people.loc[:, 'y'], self.people.loc[:, 'region_id'] = travel_op(
			self.people.loc[:, ['home_region_id', 'region_id', 'x', 'y', 'alive']].values, 
			self.regions.loc[:, ['region_id', 'xmin', 'xmax', 'ymin', 'ymax', 'travel_dom', 'travel_int_in', 'travel_int_out', 'domestic_travel_step']].values
		)

		# spread infection
		self.people.loc[:, 'infection'] = spread_op(
			self.people.loc[:, ['x', 'y', 'alive', 'infection', 'region_id']].values, 
			self.regions.loc[:, ['region_id', 'prob_of_spread', 'infection_radius']].values
		)

		# change severity
		self.people.loc[:, 'alive'], self.people.loc[:, 'infection'] = change_severity_op(
			self.people.loc[:, 'alive'].values, 
			self.people.loc[:, 'infection'].values
		)

		# social distancing
		self.people.loc[:, 'x'], self.people.loc[:, 'y'] = social_distancing_op(
			self.people.loc[:, ['x', 'y', 'alive', 'region_id']].values,
			self.regions.loc[:, ['region_id', 'xmin', 'xmax', 'ymin', 'ymax', 'social_distancing']].values
		)

	@staticmethod
	@njit
	def _get_SIR(people, regions):
		# returns the fraction of susceptible (S), Infected-unknown(I_), Infected-known (I), Removed (R) values
		# additionally sends the x,y coordinates of bar plot used in animation

		region_id, alive, infection = people[:, 0], people[:, 1], people[:, 2]
		r_region_id, r_xmax, r_ymin, r_ymax, visible_infection = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3], regions[:, 4]

		sir = np.empty(shape=(regions.shape[0], 6))

		for r in range(regions.shape[0]):
			N, S, I_, I, R = 0.0, 0, 0, 0, 0
			for p in range(people.shape[0]):
				if region_id[p] == r_region_id[r]:
					N += 1.0
					if alive[p] == 0:
						R += 1
					elif infection[p] == 0:
						S += 1
					elif infection[p] < visible_infection[r]:
						I_ += 1
					else:
						I += 1
			height = float(r_ymax[r] - r_ymin[r])
			sir[r, :] = [r_xmax[r], r_ymin[r], S*height/N, I_*height/N, I*height/N, R*height/N]
		
		return sir