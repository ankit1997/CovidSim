'''
OLD IMPLEMENTATION - TODO: REMOVE
'''


import numpy as np
import pandas as pd

import core.utils.optimized_ops as ops
from core.simulation.entity.people import PEOPLE
from core.simulation.entity.regions import REGIONS
from core.simulation.entity.medic import MEDIC
from core.simulation.validator import validate_people, validate_regions
from core.simulation.policy.policymanager import PolicyManager


class World(object):

	def __init__(self, num_people=200, T=10):
		self.num_people = num_people
		self.people = PEOPLE
		self.regions = REGIONS
		self.medics = MEDIC
		self.T = T
		self.t = 0

		self.initialize()
		validate_people(self.people)
		validate_regions(self.regions)

	def initialize(self):
		# initialize world dataframe
		print('Initializing a {}x{} world...'.format(len(self.regions), self.num_people))

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
	
	def initialize_infections(self, num_infections=5):
		# set few people with infections
		idx = self.people.sample(n=num_infections).index
		self.people.loc[idx, 'infection'] = 0.1
	
	def simulate(self):
		self.t += 1

		self.move()
		self.spread_infections()
		self.change_severity()

		# subtract daily expenses per region
		# self.regions.loc[i, 'funds']
		# for i in range(len(self.regions)):
		# 	total_active_population = self.people.groupby('region_name').sum().loc[self.regions.loc[i, 'region_name'], 'alive']
		# 	self.regions.loc[i, 'funds'] -= PolicyManager.DAILY_EXPENSE_FACTOR * total_active_population
			
	
	def move(self):
		# simulate travel

		# number of people
		N = self.people.shape[0]

		# join people and regions
		combined = pd.merge(self.people, self.regions, on='region_name', how='left')

		# get travellers indices
		alive = combined.loc[:, 'alive'] == 1
		domestic = alive & (np.random.random((N,)) < combined['travel_dom'])
		international = alive & (np.random.random((N,)) < combined['travel_int'])
		
		# get new domestic coordinates
		move_x = np.random.normal(scale=combined.loc[domestic, 'domestic_travel_step'])
		move_y = np.random.normal(scale=combined.loc[domestic, 'domestic_travel_step'])
		
		# move people and make sure no one leaves boundary while domestic travel
		combined.loc[domestic, 'x'] = ops.clip1D(ops.add1D(combined.loc[domestic, 'x'].values, move_x), combined.loc[domestic, 'xmin'].values, combined.loc[domestic, 'xmax'].values)
		combined.loc[domestic, 'y'] = ops.clip1D(ops.add1D(combined.loc[domestic, 'y'].values, move_y), combined.loc[domestic, 'ymin'].values, combined.loc[domestic, 'ymax'].values)
		
		# move domestic
		self.people.loc[domestic, ['x', 'y']] = combined.loc[domestic, ['x', 'y']]
		
		if ops.any1D(international.values):
			
			# get new location and position of people travelling internationally
			new_region_index, new_x, new_y = ops.travel_international(
				combined.loc[international, 'region_id'].values, 
				self.regions.index.values, 
				self.regions.xmin.values, 
				self.regions.xmax.values,
				self.regions.ymin.values, 
				self.regions.ymax.values
			)

			# set new attributes
			self.people.loc[international, 'region_name'] = self.regions.loc[new_region_index, 'region_name'].values
			self.people.loc[international, 'x'] = new_x
			self.people.loc[international, 'y'] = new_y
	
	def spread_infections(self):
		# infect new people

		combined = pd.merge(self.people, self.regions, on='region_name', how='left')

		# infectant = agent of infection
		# infectee = person getting infected
		infectant, infectee = ops.get_new_infections(combined.x.values, combined.y.values,
													combined.alive.values, combined.infection.values, 
													combined.infection_radius.values, combined.prob_of_spread.values)
		
		# self.people.loc[infectee, 'infection'] = self.people.loc[infectant, 'infection'].values # TEMP COMMENTED
		self.people.loc[infectee, 'infection'] = 0.2
	
	def change_severity(self):
		# modify the degree of infection
		infected = (self.people.alive == 1) & (self.people.infection > 0.0)
		self.people.loc[infected, 'infection'] += 0.01

		# when infection exceeds 1.0, then..
		dead = self.people.infection >= 1.0
		self.people.loc[dead, 'alive'] = 0