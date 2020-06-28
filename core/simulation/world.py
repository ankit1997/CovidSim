import numpy as np
import pandas as pd

from core.utils import ops
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

		self.move()
		self.spread_infections()
	
	def move(self):
		# simulate travel

		# number of people
		N = self.people.shape[0]

		# join people and regions
		combined = pd.merge(self.people, self.regions, on='region_name', how='left')

		# get travellers indices
		alive = combined.loc[:, 'alive'] == 1
		domestic = alive & (ops.random1D(N) < combined['travel_dom'])
		international = alive & (ops.random1D(N) < combined['travel_int'])
		
		# get new domestic coordinates
		move_x = ops.random_normal1D(combined.loc[domestic, 'domestic_travel_step'].values)
		move_y = ops.random_normal1D(combined.loc[domestic, 'domestic_travel_step'].values)
		
		# move people and make sure no one leaves boundary while domestic travel
		combined.loc[domestic, 'x'] = ops.clip1D(ops.add1D(combined.loc[domestic, 'x'].values, move_x), combined.loc[domestic, 'xmin'].values, combined.loc[domestic, 'xmax'].values)
		combined.loc[domestic, 'y'] = ops.clip1D(ops.add1D(combined.loc[domestic, 'y'].values, move_y), combined.loc[domestic, 'ymin'].values, combined.loc[domestic, 'ymax'].values)
		
		# move domestic
		self.people.loc[domestic, ['x', 'y']] = combined.loc[domestic, ['x', 'y']]
		
		if ops.any1D(international.values):

			new_region_index, new_x, new_y = ops.travel_international(
				combined.loc[international, 'region_id'].values, 
				self.regions.index.values, 
				self.regions.xmin.values, 
				self.regions.xmax.values,
				self.regions.ymin.values, 
				self.regions.ymax.values
			)

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
		
		self.people.loc[infectee, 'infection'] = self.people.loc[infectant, 'infection'].values