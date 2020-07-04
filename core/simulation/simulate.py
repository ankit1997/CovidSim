import numpy as np
import pandas as pd
from numba import njit
from queue import Queue
from random import random

from core.simulation.entity.people import PEOPLE
from core.simulation.entity.regions import REGIONS

class Simulator(object):

	def __init__(self, num_people):
		self.num_people = num_people
		self.people = PEOPLE
		self.regions = REGIONS
		self.frameQueue = Queue()

		self.initialize()
	
	def initialize(self):
		# initialize world dataframe
		print('Initializing a {}x{} world...'.format(len(self.regions), self.num_people))

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
	
	def call(self):

		# travel people around
		self.people.loc[:, 'x'], self.people.loc[:, 'y'], self.people.loc[:, 'region_id'] = self.travel(
			self.people.loc[:, ['home_region_id', 'region_id', 'x', 'y', 'alive']].values, 
			self.regions.loc[:, ['region_id', 'xmin', 'xmax', 'ymin', 'ymax', 'travel_dom', 'travel_int', 'domestic_travel_step']].values
		)

		# spread infection
		self.people.loc[:, 'infection'] = self.spread_infections(
			self.people.loc[:, ['x', 'y', 'alive', 'infection', 'region_id']].values, 
			self.regions.loc[:, ['region_id', 'prob_of_spread', 'infection_radius']].values
		)

		# change severity
		self.people.loc[:, 'alive'], self.people.loc[:, 'infection'] = self.change_severity(
			self.people.loc[:, 'alive'].values, 
			self.people.loc[:, 'infection'].values
		)

	@staticmethod
	@njit
	def travel(people, regions):

		home_region_id, region_id, x, y, alive = people[:, 0], people[:, 1], people[:, 2], people[:, 3], people[:, 4]
		r_region_id, r_xmin, r_xmax, r_ymin, r_ymax, r_travel_dom, r_travel_int, r_step = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3], regions[:, 4], regions[:, 5], regions[:, 6], regions[:, 7]

		for i in range(people.shape[0]):
			
			travel_dom_i, travel_int_i = -1.0, 1.0
			for j in range(regions.shape[0]):
				if region_id[i] == r_region_id[j]:
					travel_dom_i = r_travel_dom[j]
					travel_int_i = r_travel_int[j]
					break
			
			# domestic travel
			if alive[i] > 0 and travel_dom_i > random():

				# find out bounds of current region and step size for domestic travel
				xm, xM, ym, yM, step = -1.0, -1.0, -1.0, -1.0, -1.0
				for j in range(regions.shape[0]):
					if region_id[i] == r_region_id[j]:
						xm, xM, ym, yM, step = r_xmin[j], r_xmax[j], r_ymin[j], r_ymax[j], r_step[j]
						break
				
				# travel within step size 
				x[i] = x[i] + (2.0 * random() - 1.0) * step
				y[i] = y[i] + (2.0 * random() - 1.0) * step

				# clip position to within bounding box
				x[i] = xm if x[i] < xm else (xM if x[i] > xM else x[i])
				y[i] = ym if y[i] < ym else (yM if y[i] > yM else y[i])
			
			elif alive[i] > 0 and travel_int_i > random():
				
				# find new region to go to
				new_region_id, new_region_x, new_region_y = -1, -1.0, -1.0
				for j in range(regions.shape[0]):
					if home_region_id[i] != r_region_id[j] and (random() > 0.4 or j == regions.shape[0]-1):
						new_region_id = r_region_id[j]
						new_region_x = random() * (r_xmax[j] - r_xmin[j]) + r_xmin[j]
						new_region_y = random() * (r_ymax[j] - r_ymin[j]) + r_ymin[j]
				
				x[i] = new_region_x
				y[i] = new_region_y
				region_id[i] = new_region_id

		return x, y, region_id
	
	@staticmethod
	@njit
	def spread_infections(people, regions):

		x, y, alive, infection, region_id = people[:, 0], people[:, 1], people[:, 2], people[:, 3], people[:, 4]
		r_region_id, r_prob_spread, r_infection_radius = regions[:, 0], regions[:, 1], regions[:, 2]

		for i in range(people.shape[0]): # infectant
			if alive[i] == 0 or infection[i] == 0.0: # valid infectant is alive and has infection
				continue

			# in the region where i belongs, get the value of infection radius and probability of spread
			radius, prob = -1.0, -1.0
			for j in range(regions.shape[0]):
				if r_region_id[j] == region_id[i]:
					radius = r_infection_radius[j]
					prob = r_prob_spread[j]
					break
			
			for j in range(people.shape[0]): # infectee

				if alive[j] == 0 or infection[j] > 0.0: # valid infectee is alive and doesn't have infection
					continue
				
				if ((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2) <= radius ** 2 and random() <= prob:
					# infection can spread (with some probability) if uninfected people (j) are in close proximity with infected people (i)
					infection[j] = min(infection[j] + 0.1, 1.0)

		return infection
	
	@staticmethod
	@njit
	def change_severity(alive, infection):

		for i in range(alive.shape[0]):
			
			if alive[i] > 0 and infection[i] > 0.0 and infection[i] < 1.0:
				infection[i] = min(infection[i] + 0.01, 1.0)
			
			if alive[i] > 0 and infection[i] == 1.0:
				alive[i] = 0
			
		
		return alive, infection